# probablyfine-synthetic

Synthetic test bundle for exercising deterministic ranking behavior.

## Scenarios Included

- Correlated finding from both sources (`CVE-2024-0001` + `openssl`)
- High threat via EPSS (`CVE-2024-0002`)
- Build-only package deprioritization (`pytest`)
- Low threat known item (`CVE-2024-0004`)
- Unknown threat intel default (`CVE-2024-0005` absent from `threat_intel.json`)

## Inputs

- `dependabot.json`
- `ecr_findings.json`
- `threat_intel.json` (synthetic deterministic cache)
- `.probablyfine/context_public.json`
- `.probablyfine/context_internal.json`

## Run (Public Exposure Context)

```bash
PYTHONPATH=src python3 -m probablyfine.triage.normalize_findings \
  --dependabot templates/probablyfine-synthetic/dependabot.json \
  --ecr templates/probablyfine-synthetic/ecr_findings.json \
  --output templates/probablyfine-synthetic/.probablyfine/cache/normalized_findings.json

PYTHONPATH=src python3 -m probablyfine.triage.select_env_overrides \
  --context templates/probablyfine-synthetic/.probablyfine/context_public.json \
  --output templates/probablyfine-synthetic/.probablyfine/cache/env_overrides_public.json

PYTHONPATH=src python3 -m probablyfine.triage.score_and_rank \
  --normalized templates/probablyfine-synthetic/.probablyfine/cache/normalized_findings.json \
  --threat-intel templates/probablyfine-synthetic/threat_intel.json \
  --env-overrides templates/probablyfine-synthetic/.probablyfine/cache/env_overrides_public.json \
  --output-md templates/probablyfine-synthetic/.probablyfine/reports/synthetic-public.md \
  --output-json templates/probablyfine-synthetic/.probablyfine/reports/synthetic-public.json \
  --intel-fetch-performed no
```

## Run (Internal Exposure Context)

```bash
PYTHONPATH=src python3 -m probablyfine.triage.select_env_overrides \
  --context templates/probablyfine-synthetic/.probablyfine/context_internal.json \
  --output templates/probablyfine-synthetic/.probablyfine/cache/env_overrides_internal.json

PYTHONPATH=src python3 -m probablyfine.triage.score_and_rank \
  --normalized templates/probablyfine-synthetic/.probablyfine/cache/normalized_findings.json \
  --threat-intel templates/probablyfine-synthetic/threat_intel.json \
  --env-overrides templates/probablyfine-synthetic/.probablyfine/cache/env_overrides_internal.json \
  --output-md templates/probablyfine-synthetic/.probablyfine/reports/synthetic-internal.md \
  --output-json templates/probablyfine-synthetic/.probablyfine/reports/synthetic-internal.json \
  --intel-fetch-performed no
```
