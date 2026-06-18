# Cache/Report Retention Policy

This policy defines deterministic retention behavior for `.probablyfine/cache/` and `.probablyfine/reports/`.

## Directory Scope

Retention applies only to dated directories:
- `.probablyfine/cache/<YYYY-MM-DD>/`
- `.probablyfine/reports/<YYYY-MM-DD>/`

Non-dated directories are not touched.

## Default Settings

- `keep_days = 30`
- `keep_latest = 7`

Both settings are enforced together:
- directories newer than `keep_days` are retained
- the most recent `keep_latest` dated directories are retained even if older

## Cleanup Behavior

Use deterministic retention utility:

```bash
probablyfine-retention --repo /path/to/repo
```

Default is dry-run.

Apply deletion:

```bash
probablyfine-retention --repo /path/to/repo --apply
```

Optional report artifact:

```bash
probablyfine-retention --repo /path/to/repo --report-json /tmp/retention-report.json
```

## Safety Rules

- Cleanup is explicit (`--apply` required).
- Deletion is limited to valid dated directories.
- A deterministic summary (`delete_count`, `delete_dirs`) is emitted for auditability.

