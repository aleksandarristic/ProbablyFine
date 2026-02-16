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
