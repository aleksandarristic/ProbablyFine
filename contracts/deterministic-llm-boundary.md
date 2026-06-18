# Deterministic vs LLM Boundary Policy

This policy defines which `ProbablyFine` stages are strictly deterministic and where bounded LLM/Codex assistance is permitted.

## Deterministic-Only Stages

The following stages MUST remain deterministic:

1. `.probablyfine` contract discovery and schema validation
2. typed config loading and schema-version gating
3. Dependabot/ECR collection, retry/timeout controls, and cache writes
4. finding normalization and deduplication
5. threat intel fetch from allowed structured sources (EPSS/KEV)
6. context mapping to CVSSv4 Environmental metrics
7. score and rank computation
8. report/cache/run-manifest/index generation
9. retention cleanup behavior and deterministic verification harness

Deterministic means:
- identical inputs and configuration produce identical logical outputs
- no unstructured external text influences base risk computation
- no hidden state or randomization in core scoring/reporting

## Allowed LLM/Codex Stage

Only `PF-044` optional adjustment may use LLM/Codex assistance, with these constraints:

- feature flagged and disabled by default
- deterministic base score is preserved as source-of-truth
- any adjustment is emitted as separate annotation/rationale data
- mutation of final adjusted score requires explicit enabling
- all prompts/inputs/outputs must be auditable artifacts

## Prohibited LLM Usage

LLM/Codex MUST NOT be used to:
- invent CVEs, package names, versions, vectors, or fixes
- modify CVSS base metrics
- replace deterministic normalization/scoring logic
- bypass source allowlist for threat intel

## Enforcement Notes

- Config setting `processing.allow_llm_adjustment` controls whether optional adjustment stage is eligible.
- Additional explicit runtime enablement is required before any score mutation is applied.
- Policy violations should fail closed (deterministic output only).

