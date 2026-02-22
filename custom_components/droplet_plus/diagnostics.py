"""Diagnostics support for Droplet."""

from __future__ import annotations

from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.helpers.redact import async_redact_data

from . import DropletConfigEntry
from .const import VERSION

TO_REDACT = {"host", "token", "unique_id", "serial_number"}


async def async_get_config_entry_diagnostics(
    hass: HomeAssistant,
    entry: DropletConfigEntry,
) -> dict[str, Any]:
    """Return diagnostics for a config entry."""
    coordinator = entry.runtime_data

    config_data = {
        "entry_id": entry.entry_id,
        "version": entry.version,
        "domain": entry.domain,
        "integration_version": VERSION,
        "data": async_redact_data(dict(entry.data), TO_REDACT),
        "options": dict(entry.options),
    }

    device_data = {
        "model": coordinator.device_model,
        "manufacturer": coordinator.device_manufacturer,
        "firmware": coordinator.device_firmware,
        "serial_number": "**REDACTED**",
        "available": coordinator.available,
    }

    coordinator_data = {
        "lifetime_volume": coordinator.lifetime_volume,
        "hourly_volume": coordinator.hourly_volume,
        "daily_volume": coordinator.daily_volume,
        "weekly_volume": coordinator.weekly_volume,
        "monthly_volume": coordinator.monthly_volume,
        "yearly_volume": coordinator.yearly_volume,
        "flow_rate": coordinator.flow_rate,
        "server_status": coordinator.server_status,
        "signal_quality": coordinator.signal_quality,
        "water_leak_detected": coordinator.water_leak_detected,
        "water_tariff": coordinator.water_tariff,
        "water_leak_threshold": coordinator.water_leak_threshold,
    }

    buffer_data = {
        "flow_samples_count": coordinator.flow_samples_count,
        "hourly_consumption_count": coordinator.hourly_consumption_count,
        "daily_consumption_count": coordinator.daily_consumption_count,
        "hourly_flow_stats_count": coordinator.hourly_flow_stats_count,
    }

    return {
        "config": config_data,
        "device": device_data,
        "coordinator": coordinator_data,
        "buffers": buffer_data,
    }
