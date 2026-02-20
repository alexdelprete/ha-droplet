"""Sensor platform for Droplet."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


@dataclass(frozen=True, kw_only=True)
class {{ domain | replace('_', ' ') | title | replace(' ', '') }}SensorEntityDescription(SensorEntityDescription):
    """Describes a Droplet sensor entity."""

    value_fn: Callable[[dict[str, Any]], Any] | None = None


SENSOR_DESCRIPTIONS: tuple[{{ domain | replace('_', ' ') | title | replace(' ', '') }}SensorEntityDescription, ...] = (
    # TODO: Add sensor descriptions
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up sensor entities."""
    # TODO: Implement sensor setup
    pass
