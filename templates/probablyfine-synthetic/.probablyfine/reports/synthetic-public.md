# Contextual Threat-Informed Vulnerability Triage Report

## Inputs
- dependabot.json: present
- ecr_findings.json: present
- context.json: present
- threat_intel.json: present
- intel_fetch_performed: no
- intel_sources:
  - epss: synthetic-fixture
  - kev: synthetic-fixture

## Summary Counts
Total: 5
Critical: 1
High: 2
Medium: 2
Low: 0
Unknown: 0

E:A: 1
E:F: 1
E:P: 1
E:U: 1
E:X: 1

Both: 1
ECR-only: 1
Dependabot-only: 3

## Findings

| Rank | RiskScore | CVE | Package | Severity | E | SourceBucket | RuntimeRelevance | Exposure(MAV) | CR/IR/AR | CVSS4_BaseVector | CVSS4_FinalVector | FixVersion | RecommendedAction | Evidence | ScoreBreakdown |
|---:|---:|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 100 | CVE-2024-0001 | openssl | Critical | E:A | Both | runtime | MAV:N | CR:H/IR:M/AR:M | CVSS:4.0/AV:N/AC:H/AT:P/PR:N/UI:N/VC:H/VI:H/VA:H/SC:L/SI:L/SA:N | CVSS:4.0/AV:N/AC:H/AT:P/PR:N/UI:N/VC:H/VI:H/VA:H/SC:L/SI:L/SA:N/E:A/CR:H/IR:M/AR:M/MAV:N/MPR:L | 3.0.12 | Upgrade openssl to 3.0.12 | arn:aws:ecr:region:acct:finding/2001, db-1001 | S=1,T=1,X=1,I=1,R=1,F=1 |
| 2 | 86 | CVE-2024-0002 | requests | High | E:F | Dependabot-only | runtime | MAV:N | CR:H/IR:M/AR:M | CVSS:4.0/AV:N/AC:H/AT:P/PR:N/UI:N/VC:H/VI:H/VA:H/SC:L/SI:L/SA:L | CVSS:4.0/AV:N/AC:H/AT:P/PR:N/UI:N/VC:H/VI:H/VA:H/SC:L/SI:L/SA:L/E:F/CR:H/IR:M/AR:M/MAV:N/MPR:L | 2.32.4 | Upgrade requests to 2.32.4 | db-1002 | S=0.75,T=0.75,X=1,I=1,R=1,F=1 |
| 3 | 73 | CVE-2024-0003 | pytest | High | E:P | Dependabot-only | build-only | MAV:N | CR:H/IR:M/AR:M | unknown | unknown | 8.3.4 | Upgrade pytest to 8.3.4 | db-1003 | S=0.75,T=0.5,X=1,I=1,R=0.3,F=1 |
| 4 | 66 | CVE-2024-0004 | curl | Medium | E:U | ECR-only | runtime | MAV:N | CR:H/IR:M/AR:M | unknown | unknown | 8.9.1 | Upgrade curl to 8.9.1 | arn:aws:ecr:region:acct:finding/2002 | S=0.5,T=0.25,X=1,I=1,R=1,F=1 |
| 5 | 57 | CVE-2024-0005 | nginx | Medium | E:X | Dependabot-only | unknown | MAV:N | CR:H/IR:M/AR:M | unknown | unknown | unknown | Upgrade nginx; fixed version unknown in input | db-1004 | S=0.5,T=0.1,X=1,I=1,R=0.7,F=0.6 |

## Missing Data / Unknowns
- none

## Self-Check
- Counts match table rows: yes
- Sorting applied per rules: yes
- No invented CVEs/packages/versions/vectors: yes
- Base metrics unchanged: yes
- Threat mapping used only EPSS/KEV: yes
- RiskScore computed per formula: yes
