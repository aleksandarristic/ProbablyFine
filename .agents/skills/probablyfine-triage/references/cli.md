# CLI Usage

Primary pipeline command:

```bash
python3 scripts/probablyfine-triage/triage_pipeline.py
```

Scanner wrapper (multi-repo):

```bash
python3 scripts/probablyfine-triage/scanner.py /path/to/repo-a /path/to/repo-b --offline --mode parallel --workers 4
python3 scripts/probablyfine-triage/scanner.py --repo-list repos.txt --offline --summary-json scan-summary.json
python3 scripts/probablyfine-triage/scanner.py --repo-list repos.txt --offline --mode parallel --workers 4 --batch-size 25
```

Backward-compatible wrapper:

```bash
python3 scripts/probablyfine-triage/triage.py
```

## Pipeline stages

1. Normalize findings

```bash
python3 scripts/probablyfine-triage/normalize_findings.py \
  --dependabot dependabot.json \
  --ecr ecr_findings.json \
  --output normalized_findings.json
```

2. Fetch threat intel (EPSS + KEV)

```bash
python3 scripts/probablyfine-triage/fetch_threat_intel.py \
  --normalized normalized_findings.json \
  --output threat_intel.json
```

3. Select environmental overrides from context

```bash
python3 scripts/probablyfine-triage/select_env_overrides.py \
  --context context.json \
  --output env_overrides.json
```

4. Score and rank

```bash
python3 scripts/probablyfine-triage/score_and_rank.py \
  --normalized normalized_findings.json \
  --threat-intel threat_intel.json \
  --env-overrides env_overrides.json \
  --output-md contextual-threat-risk-triage.md \
  --output-json contextual-threat-risk-triage.json
```

## Offline mode

Skip internet threat fetch and emit null EPSS/KEV values:

```bash
python3 scripts/probablyfine-triage/triage_pipeline.py --offline
```

## Artifacts

- `normalized_findings.json`
- `threat_intel.json`
- `env_overrides.json`
- `contextual-threat-risk-triage.md`
- `contextual-threat-risk-triage.json`


Scanner writes per-repo run manifests to `.probablyfine/reports/<YYYY-MM-DD>/run-manifest-<run-id>.json`.

PROBABLYFINE_DEPENDABOT_FILE=/path/to/dependabot.json python3 scripts/probablyfine-triage/scanner.py /path/to/repo --offline
