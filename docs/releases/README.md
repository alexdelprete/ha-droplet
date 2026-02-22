# Release Workflow

This document describes the release workflow for the Droplet integration.

## Version Locations

Versions must be synchronized in:

1. `custom_components/droplet_plus/manifest.json` -> `"version": "X.Y.Z"`
1. `custom_components/droplet_plus/const.py` -> `VERSION = "X.Y.Z"`
1. Git tag -> `vX.Y.Z`

## Release Process

1. Update `CHANGELOG.md` with version summary
1. Create release notes file `docs/releases/vX.Y.Z.md` using the
   [Release Notes Format](#release-notes-format)
1. Ensure versions are correct in `manifest.json` and `const.py`
1. Run linting: `uvx pre-commit run --all-files`
1. Commit and push
1. Verify CI passes (lint, test, validate)
1. Create git tag: `git tag -a vX.Y.Z -m "Release vX.Y.Z"`
1. Push tag: `git push --tags`
1. Create GitHub release using the content of `docs/releases/vX.Y.Z.md`
   as the release body
1. GitHub Actions validates versions and uploads ZIP asset

## Release Notes Format

Each release has a dedicated notes file in `docs/releases/` named
`vX.Y.Z.md`. Use this template:

```markdown
# Release vX.Y.Z

[![GitHub Downloads](https://img.shields.io/github/downloads/alexdelprete/ha-droplet-plus/vX.Y.Z/total?style=for-the-badge)](https://github.com/alexdelprete/ha-droplet-plus/releases/tag/vX.Y.Z)

**Release Date:** YYYY-MM-DD

**Type:** [Major/Minor/Patch/Beta] release - Brief description.

## What's Changed

### Added
- Feature 1

### Changed
- Change 1

### Fixed
- Fix 1

**Full Changelog**:
[compare/vPREV...vX.Y.Z](https://github.com/alexdelprete/ha-droplet-plus/compare/vPREV...vX.Y.Z)
```

## Release Types

- **Major** (X.0.0): Breaking changes
- **Minor** (x.Y.0): New features, backward compatible
- **Patch** (x.y.Z): Bug fixes, backward compatible

## Important Rules

- **NEVER** create git tags or GitHub releases without explicit
  maintainer approval
- **Published releases are FROZEN** -- never modify documentation
  for released versions
- All commits on the main branch target the next release version
