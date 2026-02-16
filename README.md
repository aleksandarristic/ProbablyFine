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

## Current Code

Implementation lives in:

- `scripts/probablyfine-triage/`

Key entry points:
- `scripts/probablyfine-triage/triage_pipeline.py`
- `scripts/probablyfine-triage/triage.py`

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
