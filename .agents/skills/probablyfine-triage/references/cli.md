# CLI Usage

Primary pipeline command:

```bash
python3 scripts/probablyfine-triage/triage_pipeline.py
python3 scripts/probablyfine-triage/triage_pipeline.py --repo-root /path/to/repo
```

Scanner wrapper (multi-repo):

```bash
python3 scripts/probablyfine-triage/scanner.py /path/to/repo-a /path/to/repo-b --offline --mode parallel --workers 4
python3 scripts/probablyfine-triage/scanner.py --repo-list repos.txt --offline --summary-json scan-summary.json
python3 scripts/probablyfine-triage/scanner.py --repo-list repos.txt --offline --mode parallel --workers 4 --batch-size 25
python3 scripts/probablyfine-triage/retention.py --repo /path/to/repo --keep-days 30 --keep-latest 7
python3 scripts/probablyfine-triage/verify_determinism.py --dependabot dependabot.json --ecr ecr_findings.json --context context.json
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

With `--repo-root /path/to/repo`, default outputs are written to:
- `.probablyfine/cache/<YYYY-MM-DD>/normalized_findings.json`
- `.probablyfine/cache/<YYYY-MM-DD>/threat_intel.json`
- `.probablyfine/cache/<YYYY-MM-DD>/env_overrides.json`
- `.probablyfine/reports/<YYYY-MM-DD>/report-<timestamp>.md`
- `.probablyfine/reports/<YYYY-MM-DD>/report-<timestamp>.json`

Scanner writes per-repo run manifests to `.probablyfine/reports/<YYYY-MM-DD>/run-manifest-<run-id>.json`.

PROBABLYFINE_DEPENDABOT_FILE=/path/to/dependabot.json python3 scripts/probablyfine-triage/scanner.py /path/to/repo --offline
PROBABLYFINE_DEPENDABOT_FILE=/path/to/dependabot.json PROBABLYFINE_ECR_FILE=/path/to/ecr_findings.json python3 scripts/probablyfine-triage/scanner.py /path/to/repo --offline
PROBABLYFINE_HTTP_MAX_ATTEMPTS=3 PROBABLYFINE_HTTP_TIMEOUT_SECONDS=20 PROBABLYFINE_AWS_MAX_ATTEMPTS=3 PROBABLYFINE_AWS_TIMEOUT_SECONDS=20 python3 scripts/probablyfine-triage/scanner.py /path/to/repo --offline

## Auth precedence

Scanner validates collector auth/input configuration before collection starts.

Dependabot:
1. `PROBABLYFINE_DEPENDABOT_FILE` (must exist)
2. `GITHUB_TOKEN`
3. repo-local `dependabot.json`

ECR:
1. `PROBABLYFINE_ECR_FILE` (must exist)
2. repo-local `ecr_findings.json`
3. AWS ECR API (`boto3` + ambient AWS credentials)

5. Optional adjustment annotations stage (feature-flagged)

```bash
python3 scripts/probablyfine-triage/optional_adjustment.py \
  --report-json contextual-threat-risk-triage.json \
  --output contextual-threat-risk-llm-adjustment.json
```

Enable adjusted score application explicitly:

```bash
python3 scripts/probablyfine-triage/optional_adjustment.py \
  --report-json contextual-threat-risk-triage.json \
  --output contextual-threat-risk-llm-adjustment.json \
  --enable-adjustment
```
