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

Formal contract and schemas:

- `contracts/probablyfine-contract.md`
- `contracts/schema-versioning.md`
- `contracts/deterministic-llm-boundary.md`
- `contracts/retention-policy.md`
- `contracts/schemas/context.schema.json`
- `contracts/schemas/config.schema.json`

Typed config loader: `src/probablyfine/config_loader.py`
ECR image reference resolver (tag/digest normalization): `resolve_ecr_image_reference` in `src/probablyfine/config_loader.py`.

Validate starter contract/schemas:

```bash
python3 scripts/probablyfine-triage/validate_starter_contracts.py
```

## Starter Template

A starter `.probablyfine` bundle is available at:

- `templates/probablyfine-starter/.probablyfine/`

Bootstrap a target repo:

```bash
cp -R templates/probablyfine-starter/.probablyfine /path/to/target-repo/
```

Then edit:
- `/path/to/target-repo/.probablyfine/context.json`
- `/path/to/target-repo/.probablyfine/config.json`

Template includes:
- starter environment context (`context.json`)
- starter processing/source config (`config.json`)
- sample report snapshots under `.probablyfine/reports/2026-02-16/`

## Architecture (Planned)

Pipeline stages:
1. Collect findings from Dependabot and ECR.
2. Normalize and deduplicate deterministically.
3. Fetch deterministic threat intel (EPSS/KEV) and cache.
4. Apply environment context.
5. Score/rank and generate reports.

Normalization stage behavior:
- Correlation key is `(CVE, lowercase(package))`.
- Output is written to `normalized_findings.json` with stable sorting by `(cve, package)`.
- Source bucket is one of `Both`, `ECR-only`, `Dependabot-only`.
- Merge logic is deterministic across input ordering for severity/fix/base-vector selection.

Determinism policy:
- Prefer deterministic code for parsing, joins, scoring, caching, sorting, and report generation.
- Use Codex/LLM only where deterministic logic is impractical, and keep it bounded and auditable.

## Python App Layout

The project now follows a package-first layout:

```text
src/
  probablyfine/
    triage/
      ...
scripts/
  probablyfine-triage/
    ...compatibility wrappers...
pyproject.toml
requirements.txt
```

Primary runtime implementation lives in:

- `src/probablyfine/triage/`

Legacy script paths under `scripts/probablyfine-triage/` remain available as compatibility wrappers.

## Install And Run

Install locally:

```bash
python3 -m pip install -e .
```

Run via console entry points:

```bash
probablyfine-triage --offline
probablyfine-context
probablyfine-scan /path/to/repo-a /path/to/repo-b --offline --mode parallel --workers 4
probablyfine-scan --repo-list repos.txt --offline --summary-json scan-summary.json
probablyfine-scan --repo-list repos.txt --mode parallel --workers 4 --batch-size 25
probablyfine-retention --repo /path/to/repo --keep-days 30 --keep-latest 7
probablyfine-verify-determinism --dependabot dependabot.json --ecr ecr_findings.json --context context.json
```

Optional adjustment stage (feature-flagged):
- enable config: set `.probablyfine/config.json` `processing.allow_llm_adjustment=true`
- explicit runtime apply flag: `PROBABLYFINE_ENABLE_LLM_ADJUSTMENT=1`
- output artifact: `.probablyfine/reports/<date>/report-<timestamp>-llm-adjustment.json`

Or via modules:

```bash
python3 -m probablyfine.triage.triage_pipeline --offline
python3 -m probablyfine.triage.triage_pipeline --repo-root /path/to/repo --offline
python3 -m probablyfine.triage.context_creator
```

Compatibility wrappers still work:

```bash
python3 scripts/probablyfine-triage/triage_pipeline.py --offline
python3 scripts/probablyfine-triage/triage_pipeline.py --repo-root /path/to/repo --offline
python3 scripts/probablyfine-triage/context_creator.py
python3 scripts/probablyfine-triage/scanner.py /path/to/repo --offline
```

## Onboarding Quickstart

1. Create a target repo contract:
```bash
cp -R templates/probablyfine-starter/.probablyfine /path/to/target-repo/
```
2. Install ProbablyFine in this repository:
```bash
python3 -m pip install -e .
```
3. Choose collector input/auth mode:
```bash
# deterministic local files
export PROBABLYFINE_DEPENDABOT_FILE=/path/to/dependabot.json
export PROBABLYFINE_ECR_FILE=/path/to/ecr_findings.json

# or live Dependabot API
export GITHUB_TOKEN=ghp_...
```
4. Run scanner for one repo:
```bash
probablyfine-scan /path/to/target-repo --offline
```
5. Review dated outputs:
```bash
ls -R /path/to/target-repo/.probablyfine/cache
ls -R /path/to/target-repo/.probablyfine/reports
```

`triage_pipeline --repo-root /path/to/repo` writes default stage artifacts under:
- `.probablyfine/cache/<YYYY-MM-DD>/normalized_findings.json`
- `.probablyfine/cache/<YYYY-MM-DD>/threat_intel.json`
- `.probablyfine/cache/<YYYY-MM-DD>/env_overrides.json`
- `.probablyfine/reports/<YYYY-MM-DD>/report-<timestamp>.md`
- `.probablyfine/reports/<YYYY-MM-DD>/report-<timestamp>.json`

## Scanner Wrapper

The scanner wrapper validates `.probablyfine` contract/schema requirements per target repo and then runs the deterministic triage pipeline for each repository path provided.
It continues processing remaining repos when one repo fails validation or pipeline execution.

Per-repo outputs are written to:
- `.probablyfine/cache/<YYYY-MM-DD>/`
- `.probablyfine/reports/<YYYY-MM-DD>/`

Per-repo cache audit files are written to:
- `.probablyfine/cache/<YYYY-MM-DD>/cache-audit-<run-id>.json`

Per-repo run manifest files are written to:
- `.probablyfine/reports/<YYYY-MM-DD>/run-manifest-<run-id>.json`

Per-date run index files are written to:
- `.probablyfine/reports/<YYYY-MM-DD>/index.json`

Optional run summary output:
- `--summary-json <path>` writes deterministic per-repo status summary JSON.

Run modes:
- sequential: `probablyfine-scan /path/to/repo-a /path/to/repo-b --mode sequential`
- parallel: `probablyfine-scan /path/to/repo-a /path/to/repo-b --mode parallel --workers 4`
- batched: `probablyfine-scan --repo-list repos.txt --mode parallel --workers 4 --batch-size 25`

Retention cleanup:
- dry-run: `probablyfine-retention --repo /path/to/repo`
- apply: `probablyfine-retention --repo /path/to/repo --apply`
- optional report: `probablyfine-retention --repo /path/to/repo --report-json /tmp/retention.json`

Determinism verification harness:
- `probablyfine-verify-determinism --dependabot dependabot.json --ecr ecr_findings.json --context context.json`
- Harness runs pipeline twice with fixed timestamp injection (`PROBABLYFINE_FIXED_UTC_NOW`) and byte-compares emitted artifacts.

Dependabot collector details:
- Scanner fetches/open-alert Dependabot data and writes dated raw cache files: `.probablyfine/cache/<YYYY-MM-DD>/dependabot-raw-<timestamp>.json`.
- For deterministic local testing, set `PROBABLYFINE_DEPENDABOT_FILE=/path/to/dependabot.json` to bypass live API calls.

- For deterministic local testing of ECR input, set `PROBABLYFINE_ECR_FILE=/path/to/ecr_findings.json` to bypass live AWS API calls.

Collector retry/timeout controls (deterministic, bounded):
- HTTP/GitHub: `PROBABLYFINE_HTTP_TIMEOUT_SECONDS`, `PROBABLYFINE_HTTP_MAX_ATTEMPTS`, `PROBABLYFINE_HTTP_RETRY_SLEEP_SECONDS`, `PROBABLYFINE_GITHUB_PAGE_SLEEP_SECONDS`
- AWS/ECR: `PROBABLYFINE_AWS_TIMEOUT_SECONDS`, `PROBABLYFINE_AWS_MAX_ATTEMPTS`, `PROBABLYFINE_AWS_RETRY_SLEEP_SECONDS`

## Authentication Strategy

Collector auth preflight is validated before API collection starts.

Dependabot auth precedence when source is enabled:
1. `PROBABLYFINE_DEPENDABOT_FILE` (must exist)
2. `GITHUB_TOKEN`
3. repo-local `dependabot.json`
4. otherwise scanner fails with explicit auth error

ECR auth/input precedence when source is enabled:
1. `PROBABLYFINE_ECR_FILE` (must exist)
2. repo-local `ecr_findings.json`
3. AWS ECR API via `boto3` and ambient AWS credentials
4. otherwise scanner fails with explicit auth error

## Output Artifacts

Per repo, per date:
- `.probablyfine/cache/<YYYY-MM-DD>/dependabot-raw-<timestamp>.json`
- `.probablyfine/cache/<YYYY-MM-DD>/ecr-raw-<timestamp>.json`
- `.probablyfine/cache/<YYYY-MM-DD>/normalized_findings.json`
- `.probablyfine/cache/<YYYY-MM-DD>/threat_intel.json`
- `.probablyfine/cache/<YYYY-MM-DD>/env_overrides.json`
- `.probablyfine/cache/<YYYY-MM-DD>/cache-audit-<run-id>.json`
- `.probablyfine/reports/<YYYY-MM-DD>/report-<timestamp>.md`
- `.probablyfine/reports/<YYYY-MM-DD>/report-<timestamp>.json`
- `.probablyfine/reports/<YYYY-MM-DD>/run-manifest-<run-id>.json`
- `.probablyfine/reports/<YYYY-MM-DD>/index.json`

Large repo set control:
- `--batch-size <n>` processes repos in bounded batches/queues (`0` disables batching).

## Current Code

Key entry points:
- `src/probablyfine/triage/triage_pipeline.py`
- `src/probablyfine/triage/triage.py`

Context utility:
- `src/probablyfine/triage/context_creator.py`

Create a context file interactively:

```bash
probablyfine-context
```

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
