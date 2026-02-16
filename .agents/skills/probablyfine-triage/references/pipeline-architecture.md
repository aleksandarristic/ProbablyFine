# Pipeline Architecture

The repo follows a staged model aligned with the analyzed design direction from the shared chat.
The implementation code lives under `scripts/probablyfine-triage/`; the skill is guidance/contracts.

## Stage split

1. `scripts/probablyfine-triage/normalize_findings.py`
- Inputs: `dependabot.json`, `ecr_findings.json`
- Output: `normalized_findings.json`
- Internet: forbidden

2. `scripts/probablyfine-triage/fetch_threat_intel.py`
- Input: `normalized_findings.json`
- Output: `threat_intel.json`
- Internet: only EPSS + KEV sources

3. `scripts/probablyfine-triage/select_env_overrides.py`
- Input: `context.json`
- Output: `env_overrides.json`
- Internet: forbidden

4. `scripts/probablyfine-triage/score_and_rank.py`
- Inputs: normalized findings + threat intel + env overrides
- Outputs: `contextual-threat-risk-triage.md`, `contextual-threat-risk-triage.json`
- Internet: forbidden

5. `scripts/probablyfine-triage/triage_pipeline.py`
- Thin deterministic orchestrator running stages in fixed order

## Why this split

- Separates deterministic transforms from context mapping and report rendering.
- Makes failures isolated and easier to test with golden fixtures.
- Preserves reproducibility by caching threat intel.
