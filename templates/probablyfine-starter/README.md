# probablyfine-starter

Starter bundle for target repositories.

## Contents

- `.probablyfine/context.json`: environment/profile starter
- `.probablyfine/config.json`: source + processing starter
- `.probablyfine/cache/`: cache root placeholder
- `.probablyfine/reports/2026-02-16/`: sample report snapshots

## Usage

Copy into target repository root:

```bash
cp -R templates/probablyfine-starter/.probablyfine /path/to/target-repo/
```

Update at minimum:
- `.probablyfine/config.json`:
  - `sources.github.dependabot.repository`
  - `sources.aws.ecr.*` fields (`region`, `registry_id`, `repository`, `image`, `image_uri`)
- `.probablyfine/context.json`:
  - component/network/auth/data/control values for your environment
