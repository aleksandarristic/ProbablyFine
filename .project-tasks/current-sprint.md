# Current Sprint (Initial Execution Slice)

## Goal

Stand up the new `.probablyfine` processing model end-to-end for one repo using deterministic stages.

## In Scope

- PF-001 `.probablyfine` contract
- PF-002 context schema
- PF-003 config schema
- PF-010 scanner wrapper CLI (single repo first, multi-repo ready)
- PF-020 `.probablyfine` discovery/validation
- PF-030 Dependabot collector (raw cache)
- PF-031 ECR collector (raw cache)
- PF-040 normalize + dedupe
- PF-041 threat intel enrichment
- PF-042 context mapping
- PF-043 score + rank
- PF-050 dated report output
- PF-051 dated cache output

## Out Of Scope

- PF-044 optional LLM score adjustment
- PF-061 Codex-assisted environment authoring
- PF-071 batching/queueing

## Completed Ahead Of Scope

- PF-060 utility script to build `.probablyfine/context.json` from guided human input
- PF-092 Python packaging and app layout (`src/`, `pyproject.toml`, requirements, CLI entry points)

## Exit Criteria

- One command processes one repo that contains `.probablyfine/`.
- Cache files are present under `.probablyfine/cache/<date>/`.
- Reports are present under `.probablyfine/reports/<date>/`.
- Re-running with identical inputs produces deterministic stage outputs.
