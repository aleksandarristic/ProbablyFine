# probablyfine-triage Code

Deterministic implementation for vulnerability triage.

## Stages

1. `normalize_findings.py`
2. `fetch_threat_intel.py`
3. `select_env_overrides.py`
4. `score_and_rank.py`
5. `triage_pipeline.py` (orchestrator)

## Utilities

- `context_creator.py`: interactive generator for `.probablyfine/context.json`

Interactive mode:

```bash
python3 scripts/probablyfine-triage/context_creator.py
```

Non-interactive starter defaults:

```bash
python3 scripts/probablyfine-triage/context_creator.py --non-interactive
```

## Quick run

```bash
python3 scripts/probablyfine-triage/triage_pipeline.py
```

Offline:

```bash
python3 scripts/probablyfine-triage/triage_pipeline.py --offline
```
