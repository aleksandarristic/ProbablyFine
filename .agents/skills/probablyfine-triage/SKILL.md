---
name: probablyfine-triage
description: Correlate Dependabot + ECR scan findings, fetch EPSS/KEV intel, apply contextual CVSSv4 Threat+Environmental rules, and output a deterministic risk-scored triage report. Do not trigger for general code review tasks.
---

# Skill: probablyfine-triage

Use this skill for deterministic vulnerability triage from:
- repository dependency findings (`dependabot.json`)
- container scan findings (`ecr_findings.json`)
- deployment context (`context.json`)

This skill is the instruction/orchestration layer. Repository code lives in
`scripts/probablyfine-triage/` and follows a **staged pipeline**
(normalize -> threat intel -> env overrides -> scoring/report).

## Pipeline Components

- `scripts/probablyfine-triage/normalize_findings.py`
- `scripts/probablyfine-triage/fetch_threat_intel.py`
- `scripts/probablyfine-triage/select_env_overrides.py`
- `scripts/probablyfine-triage/score_and_rank.py`
- `scripts/probablyfine-triage/triage_pipeline.py` (orchestrator)
- `scripts/probablyfine-triage/triage.py` (backward-compatible wrapper)

## Deterministic Operating Rules

You MUST:
1. Correlate Dependabot and ECR findings.
2. Apply CVSS v4.0 Environmental metrics from `context.json`.
3. Apply CVSS v4.0 Threat metric `E` using structured intel only.
4. Compute custom deterministic RiskScore (0..100).
5. Emit strict report structure.

You MUST NOT:
- Invent CVEs, packages, versions, vectors, or scores.
- Modify CVSS Base metrics.
- Use unstructured internet chatter as threat intel.

Allowed threat intel sources only:
- `https://api.first.org/data/v1/epss`
- `https://github.com/cisagov/kev-data`

## Runtime Workflow

Run full pipeline:

```bash
python3 scripts/probablyfine-triage/triage_pipeline.py
```

Offline mode:

```bash
python3 scripts/probablyfine-triage/triage_pipeline.py --offline
```

Stage-by-stage commands are in `references/cli.md`.

## Inputs

- `dependabot.json`
- `ecr_findings.json`
- `context.json`
- optional `threat_intel.json` (cache)

If `context.json` is missing:
- `CR/IR/AR/MAV/MAC/MPR` default to `X`
- exposure and runtime relevance default to unknown

If threat fetch fails:
- `E:X`

## Stage Contracts

See `references/contracts.md` for exact shapes.

Generated artifacts:
- `normalized_findings.json`
- `threat_intel.json`
- `env_overrides.json`
- `contextual-threat-risk-triage.md`
- `contextual-threat-risk-triage.json`

## Threat Mapping (Deterministic `E`)

Order matters:
1. `cisa_kev_listed == true` -> `E:A`
2. `epss_probability >= 0.90` -> `E:A`
3. `epss_probability >= 0.70` -> `E:F`
4. `epss_probability >= 0.30` -> `E:P`
5. known `< 0.30` -> `E:U`
6. unknown -> `E:X`

Threat rank:
- `E:A=4`, `E:F=3`, `E:P=2`, `E:U=1`, `E:X=0`

## Environmental Mapping (Deterministic)

`CR/IR/AR`:
- high -> `H`
- medium -> `M`
- low -> `L`
- else -> `X`

`MAV`:
- internet reachable/public ingress flags -> `MAV:N`
- same VPC reachable -> `MAV:A`
- same host only -> `MAV:L`
- else -> `MAV:X`

`MPR`:
- none -> `N`
- user/service -> `L`
- admin -> `H`
- else -> `X`

`MAC`:
- mTLS or service-mesh policy enforced -> `H`
- internal + auth boundary not none -> `H`
- public + auth boundary none -> `L`
- else -> `X`

## CVSS Vector Rules

If Base vector exists in inputs:
- keep Base unchanged
- append `E`
- append non-`X` Environmental metrics

If Base missing:
- `CVSS4_BaseVector = unknown`
- `CVSS4_FinalVector = unknown`

## Runtime Presence

`runtime_rank`:
- runtime = 2
- unknown = 1
- build-only = 0

This affects triage/ranking only, not CVSS Base.

## Custom Risk Score (0..100)

Subscores:
- `SeveritySub`: Critical 1.00, High 0.75, Medium 0.50, Low 0.25, Unknown 0.10
- `ThreatSub`: E:A 1.00, E:F 0.75, E:P 0.50, E:U 0.25, E:X 0.10
- `ExposureSub`: MAV:N 1.00, MAV:A 0.60, MAV:L 0.30, MAV:X 0.50
- `ImpactReqSub`: any H 1.00, any M 0.70, all L 0.40, else 0.50
- `RuntimeSub`: runtime 1.00, unknown 0.70, build-only 0.30
- `FixSub`: fix known 1.00, fix missing 0.60

Formula:

```text
RiskScoreRaw = 100 * (
  0.30*SeveritySub +
  0.25*ThreatSub +
  0.15*ExposureSub +
  0.15*ImpactReqSub +
  0.10*RuntimeSub +
  0.05*FixSub
)
```

`RiskScore = round(RiskScoreRaw)` clamped to `0..100`.

## Correlation and Sorting

Dedup key:
- `(cve, lowercase(trim(package)))`

Source bucket:
- `Both`, `ECR-only`, `Dependabot-only`

Sort order (desc unless noted):
1. `RiskScore`
2. severity rank (Critical 4, High 3, Medium 2, Low 1, Unknown 0)
3. threat rank
4. source rank (Both 3, ECR-only 2, Dependabot-only 1)
5. runtime rank
6. fix rank (known 1 else 0)
7. CVE ascending
8. package ascending

## Output Format (Strict)

`contextual-threat-risk-triage.md` MUST follow:
- `templates/contextual-threat-risk-triage.template.md`

Allowed `RecommendedAction` values:
- `Upgrade <package> to <fixed_version>`
- `Upgrade <package>; fixed version unknown in input`
- `Update base image and rebuild`
- `Rebuild image to pick up upstream patches`
- `Investigate; insufficient data in inputs`

`ScoreBreakdown` format:
- `S=<SeveritySub>,T=<ThreatSub>,X=<ExposureSub>,I=<ImpactReqSub>,R=<RuntimeSub>,F=<FixSub>`

## Reference Map

- `references/cli.md`
- `references/pipeline-architecture.md`
- `references/contracts.md`
- `references/input-normalization.md`
- `references/intel-sources.md`
- `references/risk-model.md`
- `examples/`
- `templates/contextual-threat-risk-triage.template.md`
