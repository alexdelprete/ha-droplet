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
custom_components/droplet/
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
<!-- END SHARED:repo-sync -->

## Reference Documentation

- [Home Assistant Developer Docs](https://developers.home-assistant.io/)
