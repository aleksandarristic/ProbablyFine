# Input Normalization Notes

The triage script accepts common JSON shapes and normalizes into a shared finding model.

Dependabot extraction:
- Supports top-level arrays or `alerts`/`dependencies`/`findings` arrays.
- CVEs come from advisory identifiers (preferred) or CVE regex fallback.
- Package is normalized to lowercase; missing values become `unknown`.

ECR extraction:
- Supports top-level arrays or `findings`/`results` arrays.
- Reads package vulnerability details (`vulnerabilityId`, `vulnerablePackages`, CVSS vectors).
- Fix version is selected deterministically from available package fix versions.

Correlation key:
- `(cve, package)` where package is normalized lowercase and defaults to `unknown`.
