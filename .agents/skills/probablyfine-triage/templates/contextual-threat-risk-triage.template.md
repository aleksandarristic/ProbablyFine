# Contextual Threat-Informed Vulnerability Triage Report

## Inputs
- dependabot.json: present|missing
- ecr_findings.json: present|missing
- context.json: present|missing
- threat_intel.json: present|missing
- intel_fetch_performed: yes|no
- intel_sources:
  - epss: <url|missing>
  - kev: <url|missing>

## Summary Counts
Total: <int>
Critical: <int>
High: <int>
Medium: <int>
Low: <int>
Unknown: <int>

E:A: <int>
E:F: <int>
E:P: <int>
E:U: <int>
E:X: <int>

Both: <int>
ECR-only: <int>
Dependabot-only: <int>

## Findings

| Rank | RiskScore | CVE | Package | Severity | E | SourceBucket | RuntimeRelevance | Exposure(MAV) | CR/IR/AR | CVSS4_BaseVector | CVSS4_FinalVector | FixVersion | RecommendedAction | Evidence | ScoreBreakdown |
|---:|---:|---|---|---|---|---|---|---|---|---|---|---|---|---|---|

## Missing Data / Unknowns
- <bullets>

## Self-Check
- Counts match table rows: yes|no
- Sorting applied per rules: yes|no
- No invented CVEs/packages/versions/vectors: yes|no
- Base metrics unchanged: yes|no
- Threat mapping used only EPSS/KEV: yes|no
- RiskScore computed per formula: yes|no
