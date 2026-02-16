# ProbablyFine Project Tasks

This directory is the audit trail and project-management source for the
`probablyfine` scanner architecture.

## Conventions

- Task ID format: `PF-###`
- Status values: `TODO`, `IN_PROGRESS`, `BLOCKED`, `DONE`
- Priority values: `P0`, `P1`, `P2`
- Determinism tag:
  - `DET` means deterministic-only implementation
  - `LLM` means Codex/LLM-assisted logic is allowed

## Files

- `roadmap.md`: phased delivery plan
- `backlog.md`: canonical task list with acceptance criteria
- `current-sprint.md`: active execution slice
- `audit-log.md`: chronological change and decision log
- `open-questions.md`: unresolved decisions that can block implementation

## Update Rule

For every meaningful scope/status change:
1. Update `backlog.md`
2. Update `current-sprint.md` if active scope changed
3. Append one entry to `audit-log.md`
