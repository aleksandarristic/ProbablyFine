# Backlog

| ID | Status | Pri | Type | Depends | Summary | Acceptance Criteria |
|---|---|---|---|---|---|---|
| PF-001 | TODO | P0 | DET | - | Define `.probablyfine/` contract and required files | Spec doc exists for `.probablyfine/context.json`, `.probablyfine/config.json`, `.probablyfine/cache/`, `.probablyfine/reports/` |
| PF-002 | TODO | P0 | DET | PF-001 | Define JSON schema for environment context | JSON schema file validates provided example structure and required keys |
| PF-003 | TODO | P0 | DET | PF-001 | Define JSON schema for repo processing config | Schema includes ECR image locator and source settings |
| PF-004 | TODO | P1 | DET | PF-001 | Add config versioning strategy | All config files include `schema_version`; migration behavior documented |
| PF-005 | TODO | P1 | DET | PF-001 | Define deterministic/LLM boundary policy | Written policy lists which stages are strict deterministic and which may use Codex |
| PF-006 | TODO | P1 | DET | PF-001 | Define cache/report retention policy | Retention settings + cleanup behavior documented |
| PF-010 | TODO | P0 | DET | PF-001 | Build multi-repo scanner CLI wrapper | CLI accepts list of repo paths and runs processing per repo |
| PF-011 | TODO | P0 | DET | PF-010 | Add sequential and parallel modes | `--mode sequential|parallel` works; parallel worker count configurable |
| PF-012 | TODO | P1 | DET | PF-010 | Add resilient run orchestration | One repo failure does not crash whole run; final summary includes per-repo status |
| PF-013 | TODO | P1 | DET | PF-010 | Add per-repo run manifest | Manifest links run ID, start/end times, inputs, output paths |
| PF-020 | TODO | P0 | DET | PF-003 | Implement `.probablyfine` discovery + validation | Scanner fails clearly when `.probablyfine` missing or malformed |
| PF-021 | TODO | P1 | DET | PF-020 | Implement typed config loader | Config loader returns validated typed model objects |
| PF-022 | TODO | P1 | DET | PF-020 | Resolve ECR image ref from config | Parser supports registry/repo/tag or digest reference formats |
| PF-030 | TODO | P0 | DET | PF-020 | Dependabot collector (GitHub API) | Raw Dependabot payload fetched and cached with timestamped filename |
| PF-031 | TODO | P0 | DET | PF-022 | ECR collector (AWS API) | ECR findings fetched using configured image and cached as raw JSON |
| PF-032 | TODO | P1 | DET | PF-030,PF-031 | Deterministic retry/timeout/rate-limit controls | Collectors implement bounded retries and configurable timeouts |
| PF-033 | TODO | P1 | DET | PF-030,PF-031 | Data source authentication strategy | GitHub and AWS credential loading behavior documented and validated |
| PF-040 | TODO | P0 | DET | PF-030,PF-031 | Normalize + dedupe stage | Outputs deterministic `normalized_findings.json` with stable ordering |
| PF-041 | TODO | P0 | DET | PF-040 | Threat intel stage (EPSS/KEV) | CVEs enriched from allowed sources only; cached in `threat_intel.json` |
| PF-042 | TODO | P0 | DET | PF-002 | Context mapping stage for CVSS env metrics | Outputs deterministic `env_overrides.json` from context file |
| PF-043 | TODO | P0 | DET | PF-040,PF-041,PF-042 | Deterministic scoring and ranking stage | Produces stable score/rank output for same inputs |
| PF-044 | TODO | P1 | LLM | PF-043 | Optional Codex-assisted adjustment stage | Feature-flagged stage can emit rationale/additional annotations without mutating deterministic base score unless explicitly enabled |
| PF-045 | TODO | P1 | DET | PF-043 | Determinism verification harness | Same fixture inputs produce byte-stable outputs across multiple runs |
| PF-050 | TODO | P0 | DET | PF-043 | Report generation and dated output structure | Reports written under `.probablyfine/reports/<date>/report-<timestamp>.*` |
| PF-051 | TODO | P0 | DET | PF-030,PF-031,PF-041 | Cache audit trail writer | All fetched payloads written under `.probablyfine/cache/<date>/` with metadata |
| PF-052 | TODO | P1 | DET | PF-050,PF-051 | Run index generation | `.probablyfine/reports/<date>/index.json` summarizes generated reports |
| PF-060 | TODO | P1 | DET | PF-002 | Utility script to build context from human prompts | Interactive CLI creates valid `.probablyfine/context.json` |
| PF-061 | TODO | P2 | LLM | PF-060 | Codex-guided context authoring mode | Script can launch guided question flow compatible with Codex usage |
| PF-062 | TODO | P2 | DET | PF-060 | Context drift checker | Warns when context file is stale/incomplete relative to schema |
| PF-070 | TODO | P1 | DET | PF-010 | Repo list ingestion from file | Accept newline-delimited repo list file in addition to CLI args |
| PF-071 | TODO | P2 | DET | PF-011 | Repo batching and queueing | Large repo sets processed in bounded batches |
| PF-080 | TODO | P1 | DET | PF-040,PF-041,PF-043 | Unit tests for pipeline stages | Stage tests exist with fixtures and deterministic assertions |
| PF-081 | TODO | P1 | DET | PF-010,PF-030,PF-031 | Integration tests for full repo processing | End-to-end run test creates expected cache/report tree |
| PF-082 | TODO | P1 | DET | PF-081 | Failure-mode tests | Tests cover missing config, auth failures, API timeouts |
| PF-090 | TODO | P1 | DET | PF-050 | Documentation and onboarding | README covers setup, auth, run modes, outputs |
| PF-091 | TODO | P2 | DET | PF-090 | Example `.probablyfine` starter templates | Includes sample context/config files and expected report snapshots |
