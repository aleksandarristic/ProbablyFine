# Roadmap

## Phase 0: Contracts And Boundaries

- Define `.probablyfine/` directory contract and schema versioning.
- Finalize deterministic vs LLM responsibility boundaries.
- Define cache/report folder naming conventions and retention policy.

## Phase 1: Repo Scanner Wrapper

- Build top-level scanner CLI that accepts multiple repos.
- Add sequential and parallel processing modes.
- Add per-repo execution isolation and failure handling.

## Phase 2: Repo Context Discovery

- Resolve repo root.
- Locate `.probablyfine/` and validate required files.
- Load component/environment config and ECR image reference config.

## Phase 3: Deterministic Data Collection

- Fetch Dependabot findings via GitHub API.
- Fetch ECR scan findings via AWS API using configured image link.
- Cache raw source payloads under `.probablyfine/cache/<date>/`.

## Phase 4: Deterministic Processing Pipeline

- Normalize and deduplicate findings.
- Fetch deterministic threat intel (EPSS/KEV).
- Apply context mapping and compute final scores/ranks.

## Phase 5: Reporting And Audit Trail

- Generate dated report artifacts under `.probablyfine/reports/<date>/`.
- Generate structured JSON + Markdown outputs.
- Emit run manifest linking inputs, cache files, outputs, and config hashes.

## Phase 6: Environment Profile Utility

- Add utility to create/update `.probablyfine/context.json` from guided input.
- Support terminal interview mode first.
- Add optional Codex-assisted questionnaire mode.

## Phase 7: Hardening

- Unit tests and integration tests with fixtures/mocks.
- Retry, timeout, and rate-limit controls.
- Documentation and onboarding examples.
