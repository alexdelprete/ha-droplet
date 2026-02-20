"""The Droplet integration."""

from __future__ import annotations

import logging
from dataclasses import dataclass

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers import device_registry as dr

from .const import DOMAIN, MANUFACTURER, MODEL, VERSION

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[str] = ["sensor"]

type {{ domain | replace('_', ' ') | title | replace(' ', '') }}ConfigEntry = ConfigEntry[{{ domain | replace('_', ' ') | title | replace(' ', '') }}Data]


@dataclass
class {{ domain | replace('_', ' ') | title | replace(' ', '') }}Data:
    """Runtime data for the Droplet integration."""

    device_name: str


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Droplet from a config entry."""
    entry.runtime_data = {{ domain | replace('_', ' ') | title | replace(' ', '') }}Data(
        device_name=entry.title,
    )

    # Register the device
    device_registry = dr.async_get(hass)
    device_registry.async_get_or_create(
        config_entry_id=entry.entry_id,
        identifiers={(DOMAIN, entry.unique_id or entry.entry_id)},
        manufacturer=MANUFACTURER,
        model=MODEL,
        name=entry.title,
        sw_version=VERSION,
    )

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
