# Backlog

## Format

Each task is a small, readable card with:
- status
- priority
- type (`DET` or `LLM`)
- dependencies
- acceptance criteria

## Contracts And Boundaries

### PF-001 Define `.probablyfine/` contract and required files
- Status: DONE
- Priority: P0
- Type: DET
- Depends on: none
- Acceptance criteria: spec document exists for `.probablyfine/context.json`, `.probablyfine/config.json`, `.probablyfine/cache/`, `.probablyfine/reports/`.

### PF-002 Define JSON schema for environment context
- Status: DONE
- Priority: P0
- Type: DET
- Depends on: PF-001
- Acceptance criteria: JSON schema validates the provided context example structure and required keys.

### PF-003 Define JSON schema for repo processing config
- Status: DONE
- Priority: P0
- Type: DET
- Depends on: PF-001
- Acceptance criteria: schema includes ECR image locator and source settings.

### PF-004 Add config versioning strategy
- Status: DONE
- Priority: P1
- Type: DET
- Depends on: PF-001
- Acceptance criteria: all config files include `schema_version`; migration behavior documented.

### PF-005 Define deterministic/LLM boundary policy
- Status: DONE
- Priority: P1
- Type: DET
- Depends on: PF-001
- Acceptance criteria: written policy lists strict deterministic stages and allowed Codex/LLM stages.

### PF-006 Define cache/report retention policy
- Status: DONE
- Priority: P1
- Type: DET
- Depends on: PF-001
- Acceptance criteria: retention settings and cleanup behavior are documented.

## Scanner Wrapper And Orchestration

### PF-010 Build multi-repo scanner CLI wrapper
- Status: DONE
- Priority: P0
- Type: DET
- Depends on: PF-001
- Acceptance criteria: CLI accepts list of repo paths and runs processing per repo.

### PF-011 Add sequential and parallel modes
- Status: DONE
- Priority: P0
- Type: DET
- Depends on: PF-010
- Acceptance criteria: `--mode sequential|parallel` works; parallel worker count is configurable.

### PF-012 Add resilient run orchestration
- Status: DONE
- Priority: P1
- Type: DET
- Depends on: PF-010
- Acceptance criteria: one repo failure does not crash whole run; final summary includes per-repo status.

### PF-013 Add per-repo run manifest
- Status: DONE
- Priority: P1
- Type: DET
- Depends on: PF-010
- Acceptance criteria: manifest links run ID, start/end times, inputs, and output paths.

### PF-070 Repo list ingestion from file
- Status: DONE
- Priority: P1
- Type: DET
- Depends on: PF-010
- Acceptance criteria: scanner accepts newline-delimited repo list file in addition to CLI args.

### PF-071 Repo batching and queueing
- Status: DONE
- Priority: P2
- Type: DET
- Depends on: PF-011
- Acceptance criteria: large repo sets are processed in bounded batches.

## Repo Discovery And Config Loading

### PF-020 Implement `.probablyfine` discovery and validation
- Status: DONE
- Priority: P0
- Type: DET
- Depends on: PF-003
- Acceptance criteria: scanner fails clearly when `.probablyfine` is missing or malformed.

### PF-021 Implement typed config loader
- Status: DONE
- Priority: P1
- Type: DET
- Depends on: PF-020
- Acceptance criteria: config loader returns validated typed model objects.

### PF-022 Resolve ECR image reference from config
- Status: DONE
- Priority: P1
- Type: DET
- Depends on: PF-020
- Acceptance criteria: parser supports registry/repo/tag and digest reference formats.

## Data Collection

### PF-030 Dependabot collector (GitHub API)
- Status: DONE
- Priority: P0
- Type: DET
- Depends on: PF-020
- Acceptance criteria: raw Dependabot payload is fetched and cached with timestamped filename.

### PF-031 ECR collector (AWS API)
- Status: DONE
- Priority: P0
- Type: DET
- Depends on: PF-022
- Acceptance criteria: ECR findings are fetched using configured image and cached as raw JSON.

### PF-032 Deterministic retry/timeout/rate-limit controls
- Status: DONE
- Priority: P1
- Type: DET
- Depends on: PF-030, PF-031
- Acceptance criteria: collectors implement bounded retries and configurable timeouts.

### PF-033 Data source authentication strategy
- Status: DONE
- Priority: P1
- Type: DET
- Depends on: PF-030, PF-031
- Acceptance criteria: GitHub and AWS credential loading behavior is documented and validated.

## Processing Pipeline

### PF-040 Normalize and dedupe stage
- Status: DONE
- Priority: P0
- Type: DET
- Depends on: PF-030, PF-031
- Acceptance criteria: outputs deterministic `normalized_findings.json` with stable ordering.

### PF-041 Threat intel stage (EPSS/KEV)
- Status: DONE
- Priority: P0
- Type: DET
- Depends on: PF-040
- Acceptance criteria: CVEs are enriched from allowed sources only and cached in `threat_intel.json`.

### PF-042 Context mapping stage for CVSS environmental metrics
- Status: DONE
- Priority: P0
- Type: DET
- Depends on: PF-002
- Acceptance criteria: outputs deterministic `env_overrides.json` from context file.

### PF-043 Deterministic scoring and ranking stage
- Status: DONE
- Priority: P0
- Type: DET
- Depends on: PF-040, PF-041, PF-042
- Acceptance criteria: produces stable score/rank output for identical inputs.

### PF-044 Optional Codex-assisted adjustment stage
- Status: DONE
- Priority: P1
- Type: LLM
- Depends on: PF-043
- Acceptance criteria: feature-flagged stage emits rationale/annotations without mutating deterministic base score unless explicitly enabled.

### PF-045 Determinism verification harness
- Status: DONE
- Priority: P1
- Type: DET
- Depends on: PF-043
- Acceptance criteria: same fixture inputs produce byte-stable outputs across repeated runs.

## Reporting And Audit Trail

### PF-050 Report generation and dated output structure
- Status: DONE
- Priority: P0
- Type: DET
- Depends on: PF-043
- Acceptance criteria: reports are written under `.probablyfine/reports/<date>/report-<timestamp>.*`.

### PF-051 Cache audit trail writer
- Status: DONE
- Priority: P0
- Type: DET
- Depends on: PF-030, PF-031, PF-041
- Acceptance criteria: all fetched payloads are written under `.probablyfine/cache/<date>/` with metadata.

### PF-052 Run index generation
- Status: DONE
- Priority: P1
- Type: DET
- Depends on: PF-050, PF-051
- Acceptance criteria: `.probablyfine/reports/<date>/index.json` summarizes generated reports.

## Environment Context Utility

### PF-060 Utility script to build context from human prompts
- Status: DONE
- Priority: P1
- Type: DET
- Depends on: PF-002
- Acceptance criteria: interactive CLI creates valid `.probablyfine/context.json`.

### PF-061 Codex-guided context authoring mode
- Status: DONE
- Priority: P2
- Type: LLM
- Depends on: PF-060
- Acceptance criteria: script can launch guided question flow compatible with Codex usage.

### PF-062 Context drift checker
- Status: DONE
- Priority: P2
- Type: DET
- Depends on: PF-060
- Acceptance criteria: warns when context file is stale or incomplete relative to schema.

## Testing

### PF-080 Unit tests for pipeline stages
- Status: DONE
- Priority: P1
- Type: DET
- Depends on: PF-040, PF-041, PF-043
- Acceptance criteria: stage tests exist with fixtures and deterministic assertions.

### PF-081 Integration tests for full repo processing
- Status: DONE
- Priority: P1
- Type: DET
- Depends on: PF-010, PF-030, PF-031
- Acceptance criteria: end-to-end run test creates expected cache/report tree.

### PF-082 Failure-mode tests
- Status: DONE
- Priority: P1
- Type: DET
- Depends on: PF-081
- Acceptance criteria: tests cover missing config, auth failures, and API timeouts.

## Documentation

### PF-090 Documentation and onboarding
- Status: DONE
- Priority: P1
- Type: DET
- Depends on: PF-050
- Acceptance criteria: README covers setup, auth, run modes, and outputs.

### PF-091 Example `.probablyfine` starter templates
- Status: DONE
- Priority: P2
- Type: DET
- Depends on: PF-090
- Acceptance criteria: includes sample context/config files and expected report snapshots.

### PF-092 Python packaging and app layout
- Status: DONE
- Priority: P1
- Type: DET
- Depends on: none
- Acceptance criteria: repository includes `src/` package layout, `pyproject.toml`, requirements files, and CLI entry points with script-wrapper compatibility.

### PF-093 Runtime architecture docs refresh
- Status: DONE
- Priority: P2
- Type: DET
- Depends on: PF-043, PF-050, PF-090
- Acceptance criteria: README includes an explicit end-to-end runtime flow and code map for core modules/utilities.

### PF-094 Context model depth expansion
- Status: DONE
- Priority: P1
- Type: DET
- Depends on: PF-002, PF-042, PF-060
- Acceptance criteria: context schema and creator support runtime-per-package mapping and ownership metadata, and env mapping consumes the runtime section.

### PF-095 Synthetic triage fixture bundle
- Status: DONE
- Priority: P2
- Type: DET
- Depends on: PF-090, PF-091, PF-043
- Acceptance criteria: repository includes a synthetic fixture bundle with Dependabot/ECR/context/threat-intel inputs and docs showing deterministic stage execution for exposure/runtime/threat ranking examples.

## Pipeline Correctness Fixes

### PF-096 Fix `--repo-root` mode producing empty reports
- Status: TODO
- Priority: P0
- Type: DET
- Depends on: PF-043, PF-050
- Acceptance criteria: `triage_pipeline.py --repo-root` resolves `dependabot.json` and `ecr_findings.json` from `<repo-root>/.probablyfine/` when present; running the pipeline against the starter fixture produces a non-empty findings report.
- Notes: `triage_pipeline.py:154-155` hardcodes `dependabot_path=None, ecr_path=None` in the `--repo-root` branch. Both paths must be resolved conditionally from `pf_dir`.

### PF-097 Replace remaining subprocess call in `triage.py`
- Status: TODO
- Priority: P1
- Type: DET
- Depends on: PF-096
- Acceptance criteria: `src/probablyfine/triage/triage.py` invokes `triage_pipeline.main()` via direct import, not `subprocess.run`; the `probablyfine-triage` entry point no longer shells out.
- Notes: `triage.py:45` still does `subprocess.run(cmd, ...)`. This is the default CLI entry point and contradicts the subprocess-removal work done in `triage_pipeline.py`.

### PF-098 Fix `final_vector` for unknown CVSS version
- Status: TODO
- Priority: P1
- Type: DET
- Depends on: PF-043
- Acceptance criteria: when `cvss_base_version` returns `"unknown"`, `final_vector` returns `None` instead of appending CVSSv4 E: values to an unversioned or v2 vector string; the report renders `unknown` for `final_vector` in that case.
- Notes: `pipeline_common.py:726` — the ternary `(_E_TO_CVSS3 if ver == "3" else _E_TO_CVSS4)` silently falls through to CVSSv4 for any non-v3 string, including v2 vectors and malformed inputs.

### PF-099 Wire `optional_adjustment` stage into pipeline orchestrator
- Status: TODO
- Priority: P1
- Type: LLM
- Depends on: PF-044, PF-096
- Acceptance criteria: `triage_pipeline.py --repo-root` checks `config.json` for `processing.allow_llm_adjustment`; when true, runs the adjustment stage and writes output to the dated report directory; when false (default), stage is skipped entirely.
- Notes: `optional_adjustment.py` has a complete implementation but `triage_pipeline.py` never calls it. `PF-044` is marked DONE in backlog but the orchestrator integration was not completed.

### PF-100 Remove duplicate `exposure_sub` from `score_and_rank.py`
- Status: TODO
- Priority: P2
- Type: DET
- Depends on: none
- Acceptance criteria: `score_and_rank.py` removes its local `exposure_sub` definition and uses the one imported from `pipeline_common`; no functional change.
- Notes: `score_and_rank.py:66-73` redefines `exposure_sub` identically to `pipeline_common.py:687-693`, shadowing the import at line 22.

### PF-101 Add `fetch_status` to `build_threat_cache` return value
- Status: TODO
- Priority: P2
- Type: DET
- Depends on: PF-041
- Acceptance criteria: `build_threat_cache` sets `fetch_status: "ok"` in its returned dict; `fetch_threat_intel.py:main()` no longer needs to patch it in post-call; threat intel cache files produced by the orchestrator contain the field.
- Notes: `pipeline_common.py:424` — `build_threat_cache` returns a dict without `fetch_status`. `fetch_threat_intel.py:55` works around this by setting it manually. `triage_pipeline.py` calls `build_threat_cache` directly without this patch.

### PF-102 Fix `rows_count_ok` self-check to be meaningful
- Status: TODO
- Priority: P3
- Type: DET
- Depends on: PF-043
- Acceptance criteria: the self-check in the MD report verifies something that can actually fail — e.g. that the table row count equals the `summary.total` in the JSON — and returns `no` when a discrepancy exists.
- Notes: `score_and_rank.py:193` — `source_counts` and `scored_rows` are incremented in lockstep after the same `continue` guard, so this check is always `yes` and catches nothing.
