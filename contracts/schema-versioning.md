# Schema Versioning Strategy

This document defines deterministic schema-version handling for `ProbablyFine` contracts.

## Current Versions

- Context schema current version: `0.1.0`
- Config schema current version: `0.1.0`

## Required Field

All contract JSON files MUST include `schema_version`:
- `.probablyfine/context.json`
- `.probablyfine/config.json`

Validation rejects files missing `schema_version`.

## Deterministic Migration Behavior

`ProbablyFine` applies deterministic version gating before schema validation:

1. Read `schema_version`.
2. If it equals current supported version, continue.
3. If unsupported, fail with explicit version error.

For now, no automatic migrations are defined for legacy versions.
When legacy migration is introduced, migration steps must be:
- deterministic
- documented in this file
- applied before schema validation

## Forward-Compatibility Policy

- New schema versions require explicit implementation support.
- Unknown future versions are rejected instead of best-effort parsing.
- This preserves reproducibility and auditability.

