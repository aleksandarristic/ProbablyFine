# Open Questions

| ID | Status | Question | Why It Matters |
|---|---|---|---|
| Q-001 | OPEN | Should final risk score remain strictly deterministic in all modes, or allow an optional LLM adjustment layer? | Affects reproducibility and policy controls |
| Q-002 | OPEN | What is the exact format for ECR image reference in `.probablyfine/config.json` (full URI, account/repo/tag, digest)? | Needed for robust ECR lookup parser |
| Q-003 | OPEN | Should cache retention be time-based, count-based, or manual cleanup only? | Impacts disk growth and audit obligations |
| Q-004 | OPEN | What auth model should be primary for GitHub (PAT vs GitHub App) and AWS (profile vs role ARN)? | Impacts collector implementation and docs |
| Q-005 | OPEN | Should reports include SARIF output from day one or only JSON/Markdown? | Affects integration surface and scope |
| Q-006 | OPEN | Should scanner process repos in parallel by default or sequential by default? | Affects operational safety and API rate pressure |
| Q-007 | OPEN | Do we need a signed/hashed run manifest for tamper-evident audit trail? | Affects compliance and trust posture |
