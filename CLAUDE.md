# Claude Code Development Guidelines for Droplet Integration

## Critical Initial Steps

> **MANDATORY: At the START of EVERY session, you MUST read this entire CLAUDE.md file.**

**At every session start, you MUST:**

1. **Read this entire CLAUDE.md file** for project context and mandatory procedures
1. **Review recent git commits**: `git log --oneline -20`
1. **Check current status**: `git status`

## Project Overview

### What is Droplet?

A Home Assistant custom integration for Droplet.

### Integration Type

- **Type**: Hub
- **IoT Class**: Local Polling

### File Structure

```text
custom_components/droplet_plus/
├── __init__.py          # Integration setup
├── config_flow.py       # Config flow
├── const.py             # Constants
├── coordinator.py       # Data coordinator
├── sensor.py            # Sensor entities
├── diagnostics.py       # Diagnostics
├── device_trigger.py    # Device triggers
├── helpers.py           # Helper functions
├── repairs.py           # Repair flows
├── manifest.json        # Integration metadata
├── quality_scale.yaml   # Quality scale tracking
├── icons.json           # Entity icons
└── translations/        # Translations
```

<!-- BEGIN SHARED:repo-sync -->
<!-- Synced by repo-sync on 2026-02-20 -->

## Context7 for Documentation

Always use Context7 MCP tools automatically (without being asked) when:

- Generating code that uses external libraries
- Providing setup or configuration steps
- Looking up library/API documentation

Use `resolve-library-id` first to get the library ID, then `get-library-docs` to fetch documentation.

## GitHub MCP for Repository Operations

Always use GitHub MCP tools (`mcp__github__*`) for GitHub operations instead of the `gh` CLI:

- **Issues**: `issue_read`, `issue_write`, `list_issues`, `search_issues`, `add_issue_comment`
- **Pull Requests**: `list_pull_requests`, `create_pull_request`, `pull_request_read`, `merge_pull_request`
- **Reviews**: `pull_request_review_write`, `add_comment_to_pending_review`
- **Repositories**: `search_repositories`, `get_file_contents`, `list_branches`, `list_commits`
- **Releases**: `list_releases`, `get_latest_release`, `list_tags`

Benefits over `gh` CLI:

- Direct API access without shell escaping issues
- Structured JSON responses
- Better error handling
- No subprocess overhead

## Coding Standards

### Data Storage Pattern

**DO use `runtime_data`** (modern pattern):

```python
entry.runtime_data = MyData(device_name=name)
```

**DO NOT use `hass.data[DOMAIN]`** (deprecated pattern)

### Logging

Use structured logging:

```python
_LOGGER.debug("Sensor %s subscribed to %s", key, topic)
```

**DO NOT** use f-strings in logger calls (deferred formatting is more efficient)

### Type Hints

Always use type hints for function signatures.

## Pre-Commit Configuration

Linting tools and settings are defined in `.pre-commit-config.yaml`:

| Hook        | Tool                           | Purpose                      |
| ----------- | ------------------------------ | ---------------------------- |
| ruff        | `ruff check --no-fix`          | Python linting               |
| ruff-format | `ruff format --check`          | Python formatting            |
| jsonlint    | `uvx --from demjson3 jsonlint` | JSON validation              |
| yamllint    | `uvx yamllint -d "{...}"`      | YAML linting (inline config) |
| pymarkdown  | `pymarkdown scan`              | Markdown linting             |

All hooks use `language: system` (local tools) with `verbose: true` for visibility.

## Pre-Commit Checks (MANDATORY)

> **CRITICAL: ALWAYS run pre-commit checks before ANY git commit.**
> This is a hard rule - no exceptions. Never commit without passing all checks.

```bash
uvx pre-commit run --all-files
```

Or run individual tools:

```bash
# Python formatting and linting
ruff format .
ruff check . --fix

# Markdown linting
pymarkdown scan .
```

All checks must pass before committing. This applies to ALL commits, not just releases.

### Windows Shell Notes

When running shell commands on Windows, stray `nul` files may be created (Windows null device artifact).
Check for and delete them after command execution:

```bash
rm nul  # if it exists
```

## Testing

> **CRITICAL: NEVER run pytest locally. The local environment cannot be set up correctly for
> Home Assistant integration tests. ALWAYS use GitHub Actions CI to run tests.**

To run tests:

1. Commit and push changes to the repository
1. GitHub Actions will automatically run the test workflow
1. Check the workflow results in the Actions tab or use `mcp__github__*` tools

> **CRITICAL: NEVER modify production code to make tests pass. Always fix the tests instead.**
> Production code is the source of truth. If tests fail, the tests are wrong - not the production code.
> The only exception is when production code has an actual bug that tests correctly identified.

## Quality Scale Tracking (MUST DO)

This integration tracks [Home Assistant Quality Scale][qs] rules in `quality_scale.yaml`.

**When implementing new features or fixing bugs:**

1. Check if the change affects any quality scale rules
1. Update `quality_scale.yaml` status accordingly:
   - `done` - Rule is fully implemented
   - `todo` - Rule needs implementation
   - `exempt` with `comment` - Rule doesn't apply (explain why)
1. Aim to complete all Bronze tier rules first, then Silver, Gold, Platinum

[qs]: https://developers.home-assistant.io/docs/core/integration-quality-scale/

## Release Management - CRITICAL

> **STOP: NEVER create git tags or GitHub releases without explicit user command.**
> This is a hard rule. Always stop after commit/push and wait for user instruction.

**Published releases are FROZEN** - Never modify documentation for released versions.

**Master branch = Next Release** - All commits target the next version with version bumped
in manifest.json and const.py.

### Version Bumping Rules

> **IMPORTANT: Do NOT bump version during a session. All changes go into the CURRENT unreleased version.**

- The version in `manifest.json` and `const.py` represents the NEXT release being prepared
- **NEVER bump version until user commands "tag and release"**
- Multiple features/fixes can be added to the same unreleased version
- Only bump to a NEW version number AFTER the current version is released

### Version Locations (Must Be Synchronized)

1. `custom_components/droplet_plus/manifest.json` → `"version": "X.Y.Z"`
1. `custom_components/droplet_plus/const.py` → `VERSION = "X.Y.Z"`

### Complete Release Workflow

> **IMPORTANT: Version Validation**
> The release workflow VALIDATES that tag, manifest.json, and const.py versions all match.
> You MUST update versions BEFORE creating the release, not after.

| Step | Tool           | Action                                                                  |
| ---- | -------------- | ----------------------------------------------------------------------- |
| 1    | Edit           | Update `CHANGELOG.md` with version summary                              |
| 2    | Edit           | Ensure `manifest.json` and `const.py` have correct version              |
| 3    | Bash           | Run linting: `uvx pre-commit run --all-files`                           |
| 4    | Bash           | `git add . && git commit -m "..."`                                      |
| 5    | Bash           | `git push`                                                              |
| 6    | **STOP**       | Wait for user "tag and release" command                                 |
| 7    | **CI Check**   | Verify ALL CI workflows pass (see CI Verification below)                |
| 8    | **Checklist**  | Display Release Readiness Checklist (see below)                         |
| 9    | Bash           | `git tag -a vX.Y.Z -m "Release vX.Y.Z"`                                |
| 10   | Bash           | `git push --tags`                                                       |
| 11   | gh CLI         | `gh release create vX.Y.Z --title "vX.Y.Z" --notes "$(RELEASE_NOTES)"` |
| 12   | GitHub Actions | Validates versions match, then auto-uploads ZIP asset                   |
| 13   | Edit           | Bump versions in `manifest.json` and `const.py` to next version         |

### CI Verification (MANDATORY)

> **CRITICAL: Before tagging/releasing, ALWAYS verify ALL CI workflows are passing.**
> Use GitHub MCP tools to list workflow runs, then use `gh` CLI to get detailed logs if needed.
> NEVER proceed if any workflow is failing.

**Verification steps:**

1. Use `mcp__GitHub_MCP_Remote__actions_list` to list recent workflow runs:

   ```text
   actions_list(method="list_workflow_runs", owner="alexdelprete", repo="ha-droplet")
   ```

1. Check that ALL workflows show `conclusion: "success"`:
   - Lint workflow
   - Validate workflow
   - Tests workflow

1. If any workflow is failing, use `gh` CLI to get detailed failure logs:

   ```bash
   # View failed run logs (replace <run_id> with actual ID from step 1)
   gh run view <run_id> --log-failed

   # Or view full logs for a specific run
   gh run view <run_id> --log
   ```

1. Fix failing tests/issues, commit, push, and re-verify before proceeding

### Release Notes Format (MANDATORY)

When creating a release, use this format for the release notes:

```markdown
# Release vX.Y.Z

[![GitHub Downloads](https://img.shields.io/github/downloads/alexdelprete/ha-droplet/vX.Y.Z/total?style=for-the-badge)](https://github.com/alexdelprete/ha-droplet/releases/tag/vX.Y.Z)

**Release Date:** YYYY-MM-DD

**Type:** [Major/Minor/Patch] release - Brief description.

## What's Changed

### ✨ Added
- Feature 1

### 🔄 Changed
- Change 1

### 🐛 Fixed
- Fix 1

**Full Changelog**: https://github.com/alexdelprete/ha-droplet/compare/vPREV...vX.Y.Z
```

### Release Readiness Checklist (MANDATORY)

> **When user commands "tag and release", ALWAYS display this checklist BEFORE proceeding.**

```markdown
## Release Readiness Checklist

| Item | Status |
|------|--------|
| Version in `manifest.json` | X.Y.Z |
| Version in `const.py` | X.Y.Z |
| CHANGELOG.md updated | Updated |
| GitHub Actions (lint/test/validate) | PASSING |
| Working tree clean | Clean |
| Git tag | vX.Y.Z created/pushed |
```

Verify ALL items before proceeding with tag creation. If any item fails, fix it first.

## Do's and Don'ts

**DO:**

- Run `uvx pre-commit run --all-files` before EVERY commit
- Read CLAUDE.md at session start
- Use `runtime_data` for data storage (not `hass.data[DOMAIN]`)
- Use `@callback` decorator for message handlers
- Log with `%s` formatting (not f-strings)
- Handle missing data gracefully
- Update both manifest.json AND const.py for version bumps
- Get approval before creating tags/releases

**NEVER:**

- Commit without running pre-commit checks first
- Modify production code to make tests pass - fix the tests instead
- Use `hass.data[DOMAIN][entry_id]` - use `runtime_data` instead
- Shadow Python builtins (A001)
- Use f-strings in logging (G004)
- Create git tags or GitHub releases without explicit user instruction
- Forget to update VERSION in both manifest.json AND const.py
- Use blocking calls in async context
- Close GitHub issues without explicit user instruction

<!-- END SHARED:repo-sync -->

## Reference Documentation

- [Home Assistant Developer Docs](https://developers.home-assistant.io/)
