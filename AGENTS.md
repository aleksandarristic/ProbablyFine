# AGENTS.md

Project-specific working agreements for contributors and coding agents.

## Scope

This repository builds the `ProbablyFine` scanner and related tooling.

- Skill files under `.agents/skills/` are instruction-side artifacts.
- Runtime implementation belongs in repository code (primarily `scripts/`).

## Engineering Rules

1. Prefer deterministic implementations.
2. Treat LLM/Codex-assisted logic as optional and bounded.
3. Never invent vulnerability facts (CVE/package/version/fix/vector).
4. Preserve auditability of inputs, transformations, and outputs.
5. Keep stage contracts explicit (JSON schemas or documented contracts).

## Pipeline Direction

Target per-repo processing root is `.probablyfine/`.

Expected capabilities:
- find and validate `.probablyfine/`
- collect Dependabot + ECR findings
- normalize and dedupe
- fetch EPSS/KEV intel
- apply environment context
- score/rank
- emit dated cache + reports

## Task Tracking (Required)

For substantial work, update `.project-tasks/`:
- update task statuses in `backlog.md`
- keep `current-sprint.md` aligned with active scope
- append decisions/progress in `audit-log.md`

## Project Management System

Project management for this repository lives under `.project-tasks/` and is the
source of truth for planning, execution state, and historical decisions.

### Conventions

- Task ID format: `PF-###`
- Status values: `TODO`, `IN_PROGRESS`, `BLOCKED`, `DONE`
- Priority values: `P0`, `P1`, `P2`
- Type values:
  - `DET` for deterministic-only implementation
  - `LLM` where bounded Codex/LLM assistance is allowed

### Canonical Files

- `.project-tasks/roadmap.md`: phase-level delivery plan
- `.project-tasks/backlog.md`: canonical task list with dependencies and acceptance criteria
- `.project-tasks/current-sprint.md`: active scope and exit criteria
- `.project-tasks/audit-log.md`: chronological record of decisions and meaningful changes
- `.project-tasks/open-questions.md`: unresolved decisions that can affect implementation
- `.project-tasks/README.md`: formatting and update rules for this system

### Operating Workflow

For each meaningful scope or status change:
1. Update task state in `.project-tasks/backlog.md`.
2. Update `.project-tasks/current-sprint.md` when active scope changes.
3. Append a dated entry to `.project-tasks/audit-log.md`.

Keep acceptance criteria explicit in backlog task cards. If execution is blocked
by unresolved design or policy choices, record it in `.project-tasks/open-questions.md`
and reference the relevant task IDs.

## Change Safety

- Avoid destructive git commands unless explicitly requested.
- Do not revert unrelated user changes.
- Keep changes minimal and focused to requested scope.

## Documentation Expectations

When adding or changing behavior:
- update `README.md` (user-facing overview)
- update stage docs in `.agents/skills/probablyfine-triage/references/` when relevant
- ensure commands and paths are accurate

## Testing Expectations

- At minimum, run syntax checks for changed Python code.
- For pipeline changes, run a smoke test and verify outputs are generated.
- Call out untested areas explicitly when full verification is not possible.
