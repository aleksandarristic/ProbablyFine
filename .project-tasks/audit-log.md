# Audit Log

## 2026-02-16

- Initialized project-management directory `.project-tasks/`.
- Added roadmap, prioritized backlog, current sprint definition, and open questions.
- Captured the new target architecture:
  - per-repo `.probablyfine/` contract
  - deterministic multi-stage processing pipeline
  - dated cache and report audit trails
  - optional Codex/LLM usage only for hard-to-determinize tasks
  - multi-repo wrapper with sequential/parallel execution modes
- Added repository-level `README.md` documenting project purpose, `.probablyfine` contract, architecture direction, and task tracking references.
- Added repository-level `AGENTS.md` with project working agreements (determinism-first, code-vs-skill boundary, and required task/audit updates).
- Added starter template bundle at `templates/probablyfine-starter/.probablyfine/` with `context.json`, `config.json`, cache root placeholder, and sample report snapshots.
- Updated `README.md` with bootstrap instructions for copying the `.probablyfine` starter into target repositories.
- Marked task `PF-091` as `DONE` in `.project-tasks/backlog.md`.
- Reworked `.project-tasks/backlog.md` from table format to human-readable section/card markdown while preserving IDs, dependencies, priorities, and acceptance criteria.
- Reworked `.project-tasks/open-questions.md` from table format to human-readable section/card markdown.
- Updated `.project-tasks/README.md` to define the new non-table backlog style.
- Implemented `scripts/probablyfine-triage/context_creator.py` as deterministic interactive utility for creating `.probablyfine/context.json`.
- Added utility usage docs to `scripts/probablyfine-triage/README.md` and root `README.md`.
- Marked task `PF-060` as `DONE` in `.project-tasks/backlog.md`.
- Updated `.project-tasks/current-sprint.md` to note `PF-060` as completed ahead of original scope.
