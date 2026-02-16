# Open Questions

## Q-001 Deterministic-only score vs optional LLM-adjusted score
- Status: OPEN
- Question: Should final risk score remain strictly deterministic in all modes, or allow an optional LLM adjustment layer?
- Why it matters: affects reproducibility and policy controls.

## Q-002 ECR image reference format in `.probablyfine/config.json`
- Status: OPEN
- Question: What is the canonical format for ECR image references (full URI, account/repo/tag, digest)?
- Why it matters: required for robust ECR lookup parser behavior.

## Q-003 Cache retention policy
- Status: OPEN
- Question: Should retention be time-based, count-based, or manual cleanup only?
- Why it matters: impacts disk growth and audit obligations.

## Q-004 Authentication model for data sources
- Status: OPEN
- Question: What should be primary auth model for GitHub (PAT vs GitHub App) and AWS (profile vs role ARN)?
- Why it matters: impacts collector implementation and user documentation.

## Q-005 Report formats for initial release
- Status: OPEN
- Question: Should reports include SARIF output from day one or only JSON/Markdown?
- Why it matters: affects integration surface and scope.

## Q-006 Default execution mode
- Status: OPEN
- Question: Should scanner process repos in parallel by default or sequential by default?
- Why it matters: impacts operational safety and API rate pressure.

## Q-007 Tamper-evident audit requirement
- Status: OPEN
- Question: Do we need signed or hashed run manifests for tamper-evident audit trail?
- Why it matters: affects compliance posture and trust guarantees.
