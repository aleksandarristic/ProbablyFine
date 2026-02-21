# `.probablyfine/` Repository Contract

This document defines the minimum deterministic contract for repositories processed by `ProbablyFine`.

## Required Layout

```text
<repo>/
  .probablyfine/
    context.json
    config.json
    cache/
    reports/
```

## Required Files And Directories

- `.probablyfine/context.json`
  - Environment and deployment context consumed by contextual scoring logic.
  - Must satisfy `contracts/schemas/context.schema.json`.
- `.probablyfine/config.json`
  - Source and processing configuration for scanners/collectors/pipeline orchestration.
  - Must satisfy `contracts/schemas/config.schema.json`.
- `.probablyfine/cache/`
  - Root for dated fetched and derived artifacts.
  - Expected dated structure: `.probablyfine/cache/<YYYY-MM-DD>/...`.
- `.probablyfine/reports/`
  - Root for dated emitted reports.
  - Expected dated structure: `.probablyfine/reports/<YYYY-MM-DD>/report-<timestamp>.md|json`.

## Versioning

- `context.json` MUST include `schema_version`.
- `config.json` MUST include `schema_version`.
- Current supported schema version is `0.1.0`.
- Deterministic migration policy is defined in `contracts/schema-versioning.md`.

## Validation

Use deterministic local validation against starter examples:

```bash
python3 scripts/probablyfine-triage/validate_starter_contracts.py
```

This verifies:
- required `.probablyfine` paths exist in the starter template
- starter `context.json` conforms to the context schema
- starter `config.json` conforms to the config schema
