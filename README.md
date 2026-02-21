# ProbablyFine

`ProbablyFine` is a deterministic vulnerability triage project that correlates scanner outputs and deployment context to produce actionable, auditable risk reports.

## Objective

Given a repository, process security findings by combining:
- GitHub Dependabot alerts
- AWS ECR image scan findings
- deterministic threat intel (EPSS + CISA KEV)
- environment context from `.probablyfine/context.json`

Then produce dated, auditable reports and cached source artifacts.

## Target Repo Contract

Each scanned repository is expected to include:

```text
<repo>/
  .probablyfine/
    context.json
    config.json
    cache/
      <YYYY-MM-DD>/
        ...raw and derived artifacts...
    reports/
      <YYYY-MM-DD>/
        report-<timestamp>.md
        report-<timestamp>.json
```

Planned behaviors:
- Cache all fetched/derived data under `.probablyfine/cache/<date>/`.
- Write all reports under `.probablyfine/reports/<date>/`.
- Preserve an audit trail per run.

Formal contract and schemas:

- `contracts/probablyfine-contract.md`
- `contracts/schemas/context.schema.json`
- `contracts/schemas/config.schema.json`

Validate starter contract/schemas:

```bash
python3 scripts/probablyfine-triage/validate_starter_contracts.py
```

## Starter Template

A starter `.probablyfine` bundle is available at:

- `templates/probablyfine-starter/.probablyfine/`

Bootstrap a target repo:

```bash
cp -R templates/probablyfine-starter/.probablyfine /path/to/target-repo/
```

Then edit:
- `/path/to/target-repo/.probablyfine/context.json`
- `/path/to/target-repo/.probablyfine/config.json`

Template includes:
- starter environment context (`context.json`)
- starter processing/source config (`config.json`)
- sample report snapshots under `.probablyfine/reports/2026-02-16/`

## Architecture (Planned)

Pipeline stages:
1. Collect findings from Dependabot and ECR.
2. Normalize and deduplicate deterministically.
3. Fetch deterministic threat intel (EPSS/KEV) and cache.
4. Apply environment context.
5. Score/rank and generate reports.

Determinism policy:
- Prefer deterministic code for parsing, joins, scoring, caching, sorting, and report generation.
- Use Codex/LLM only where deterministic logic is impractical, and keep it bounded and auditable.

## Python App Layout

The project now follows a package-first layout:

```text
src/
  probablyfine/
    triage/
      ...
scripts/
  probablyfine-triage/
    ...compatibility wrappers...
pyproject.toml
requirements.txt
```

Primary runtime implementation lives in:

- `src/probablyfine/triage/`

Legacy script paths under `scripts/probablyfine-triage/` remain available as compatibility wrappers.

## Install And Run

Install locally:

```bash
python3 -m pip install -e .
```

Run via console entry points:

```bash
probablyfine-triage --offline
probablyfine-context
probablyfine-scan /path/to/repo-a /path/to/repo-b --offline --mode parallel --workers 4
probablyfine-scan --repo-list repos.txt --offline --summary-json scan-summary.json
```

Or via modules:

```bash
python3 -m probablyfine.triage.triage_pipeline --offline
python3 -m probablyfine.triage.context_creator
```

Compatibility wrappers still work:

```bash
python3 scripts/probablyfine-triage/triage_pipeline.py --offline
python3 scripts/probablyfine-triage/context_creator.py
python3 scripts/probablyfine-triage/scanner.py /path/to/repo --offline
```

## Scanner Wrapper

The scanner wrapper validates `.probablyfine` contract/schema requirements per target repo and then runs the deterministic triage pipeline for each repository path provided.
It continues processing remaining repos when one repo fails validation or pipeline execution.

Per-repo outputs are written to:
- `.probablyfine/cache/<YYYY-MM-DD>/`
- `.probablyfine/reports/<YYYY-MM-DD>/`

Per-repo run manifest files are written to:
- `.probablyfine/reports/<YYYY-MM-DD>/run-manifest-<run-id>.json`

Optional run summary output:
- `--summary-json <path>` writes deterministic per-repo status summary JSON.

## Current Code

Key entry points:
- `src/probablyfine/triage/triage_pipeline.py`
- `src/probablyfine/triage/triage.py`

Context utility:
- `src/probablyfine/triage/context_creator.py`

Create a context file interactively:

```bash
probablyfine-context
```

Current scripts support the staged triage flow with local inputs and deterministic outputs.

## Project Management

Task planning and audit trail are maintained in:

- `.project-tasks/backlog.md`
- `.project-tasks/roadmap.md`
- `.project-tasks/current-sprint.md`
- `.project-tasks/open-questions.md`
- `.project-tasks/audit-log.md`

## Next Delivery Milestones

- Formalize `.probablyfine/context.json` and `.probablyfine/config.json` schemas.
- Implement scanner wrapper for multi-repo execution (sequential/parallel).
- Integrate direct Dependabot/ECR collection into dated cache structure.
- Add context creation utility from guided human input.
