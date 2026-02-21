# JSON Contracts

## `.probablyfine` Input Contract

Repository-level contract and schemas are defined in:

- `contracts/probablyfine-contract.md`
- `contracts/schemas/context.schema.json`
- `contracts/schemas/config.schema.json`

## `normalized_findings.json`

```json
{
  "generated_at": "ISO-8601",
  "inputs": {
    "dependabot.json": "present|missing",
    "ecr_findings.json": "present|missing"
  },
  "items": [
    {
      "cve": "CVE-YYYY-NNNN",
      "package": "string",
      "severity": "critical|high|medium|low|unknown",
      "fix_version": "string|null",
      "cvss4_base_vector": "string|null",
      "sources": ["Dependabot", "ECR"],
      "source_bucket": "Both|ECR-only|Dependabot-only",
      "evidence_ids": ["string"]
    }
  ]
}
```

## `threat_intel.json`

```json
{
  "generated_at": "ISO-8601|null",
  "sources": {
    "epss": "https://api.first.org/data/v1/epss",
    "kev": "https://github.com/cisagov/kev-data"
  },
  "items": [
    {
      "cve": "CVE-YYYY-NNNN",
      "epss_probability": 0.0,
      "epss_percentile": 0.0,
      "cisa_kev_listed": false,
      "kev_date_added": "YYYY-MM-DD|null",
      "kev_due_date": "YYYY-MM-DD|null"
    }
  ]
}
```

## `env_overrides.json`

```json
{
  "generated_at": "ISO-8601",
  "source": "context.json",
  "context_json": "present|missing",
  "overrides": {
    "CR": "CR:H|CR:M|CR:L|CR:X",
    "IR": "IR:H|IR:M|IR:L|IR:X",
    "AR": "AR:H|AR:M|AR:L|AR:X",
    "MAV": "MAV:N|MAV:A|MAV:L|MAV:X",
    "MAC": "MAC:H|MAC:L|MAC:X",
    "MPR": "MPR:N|MPR:L|MPR:H|MPR:X",
    "exposure": "public|internal|unknown"
  },
  "runtime_presence_default": "runtime|unknown|build-only",
  "runtime_presence_by_package": {
    "package": "runtime|unknown|build-only"
  },
  "rationale": {
    "CR": "string",
    "IR": "string",
    "AR": "string",
    "MAV": "string",
    "MAC": "string",
    "MPR": "string"
  }
}
```
