# Deterministic Intel Sources

Only these sources are allowed:
- EPSS API: `https://api.first.org/data/v1/epss`
- CISA KEV repository: `https://github.com/cisagov/kev-data`

Implementation notes:
- EPSS is queried by CVE list (`?cve=CVE-1,CVE-2,...`).
- KEV is read from official data (`known_exploited_vulnerabilities.json`) in the CISA KEV repo.
- If fetch fails, triage must set `E:X` for unknown threat maturity.
- Never use blog/news/chatter pages for threat mapping.
