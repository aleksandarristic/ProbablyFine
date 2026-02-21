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
- Repackaged runtime code into `src/probablyfine/triage/` and added Python packaging metadata in `pyproject.toml`.
- Added `requirements.txt` and `requirements-dev.txt`.
- Added console entry points: `probablyfine-triage`, `probablyfine-triage-legacy`, and `probablyfine-context`.
- Converted files in `scripts/probablyfine-triage/` into compatibility wrappers to preserve script-based execution.
- Updated docs for package-first usage and install/run commands.
- Marked task `PF-092` as `DONE` and aligned current sprint notes.

## 2026-02-21

- Added formal `.probablyfine` input contract document at `contracts/probablyfine-contract.md`.
- Added JSON schemas:
  - `contracts/schemas/context.schema.json`
  - `contracts/schemas/config.schema.json`
- Added deterministic starter schema/contract validation utility:
  - `scripts/probablyfine-triage/validate_starter_contracts.py`
- Updated `README.md` and `.agents/skills/probablyfine-triage/references/contracts.md` with schema/contract references and validation command.
- Marked tasks `PF-001`, `PF-002`, and `PF-003` as `DONE`.
- Updated current sprint progress notes to include `PF-001`/`PF-002`/`PF-003` completions.
- Implemented scanner wrapper CLI in `src/probablyfine/scanner.py` with multi-repo path input and per-repo pipeline execution.
- Added scanner compatibility wrapper at `scripts/probablyfine-triage/scanner.py` and console script entry point `probablyfine-scan`.
- Implemented deterministic `.probablyfine` discovery/validation in `src/probablyfine/contracts.py` and reused it from `scripts/probablyfine-triage/validate_starter_contracts.py`.
- Updated scanner/CLI docs in `README.md`, `scripts/probablyfine-triage/README.md`, and `.agents/skills/probablyfine-triage/references/cli.md`.
- Marked tasks `PF-010` and `PF-020` as `DONE`.
- Added `--mode sequential|parallel` and `--workers` support to scanner (`PF-011`).
- Added per-repo run manifest emission at `.probablyfine/reports/<date>/run-manifest-<run-id>.json` with run metadata (`PF-013`).
- Updated scanner documentation and CLI references for parallel mode and manifest outputs.
- Marked tasks `PF-011` and `PF-013` as `DONE` and aligned current sprint tracking.
- Added scanner repo-list ingestion via `--repo-list` for newline-delimited repo path files (`PF-070`).
- Added explicit resilient orchestration summary output with optional `--summary-json` containing per-repo statuses (`PF-012`).
- Preserved fail-forward behavior: scanner continues processing remaining repos when individual repos fail validation or pipeline execution.
- Updated scanner docs/CLI references for `--repo-list` and `--summary-json`.
- Marked tasks `PF-012` and `PF-070` as `DONE` and aligned sprint tracking.
