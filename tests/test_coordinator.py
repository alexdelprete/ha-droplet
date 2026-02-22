"""Tests for Droplet coordinator."""

from __future__ import annotations

from datetime import timedelta
from unittest.mock import MagicMock

import pytest
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.droplet.const import EVENT_WATER_LEAK_CLEARED, EVENT_WATER_LEAK_DETECTED
from homeassistant.core import HomeAssistant
from homeassistant.util import dt as dt_util


async def test_on_update_captures_delta(
    hass: HomeAssistant,
    mock_setup_entry: MockConfigEntry,
    mock_droplet: MagicMock,
) -> None:
    """Test _on_update captures volume delta and flow rate."""
    coordinator = mock_setup_entry.runtime_data

    mock_droplet.get_flow_rate.return_value = 3.0
    mock_droplet.get_volume_delta.return_value = 100.0  # mL

    # Simulate pydroplet accumulating 100 mL
    mock_droplet._accumulated_volumes["lifetime"] = 100.0
    coordinator._on_update(None)

    assert coordinator.flow_rate == 3.0
    assert coordinator.volume_delta == 100.0
    assert coordinator.lifetime_volume == pytest.approx(0.1)  # 100 mL = 0.1 L


async def test_volume_properties_combine_baseline_and_accumulator(
    hass: HomeAssistant,
    mock_setup_entry: MockConfigEntry,
    mock_droplet: MagicMock,
) -> None:
    """Test volume properties combine baseline with pydroplet accumulator."""
    coordinator = mock_setup_entry.runtime_data

    # Set baseline from persistence
    coordinator._baseline_hourly = 5.0
    coordinator._baseline_daily = 100.0
    coordinator._baseline_lifetime = 8500.0

    # Simulate pydroplet accumulated volume (in mL)
    mock_droplet._accumulated_volumes["hourly"] = 500.0  # 0.5 L
    mock_droplet._accumulated_volumes["daily"] = 1000.0  # 1.0 L
    mock_droplet._accumulated_volumes["lifetime"] = 2000.0  # 2.0 L

    assert coordinator.hourly_volume == pytest.approx(5.5)
    assert coordinator.daily_volume == pytest.approx(101.0)
    assert coordinator.lifetime_volume == pytest.approx(8502.0)


async def test_on_update_skips_when_unavailable(
    hass: HomeAssistant,
    mock_setup_entry: MockConfigEntry,
    mock_droplet: MagicMock,
) -> None:
    """Test _on_update skips processing when device unavailable."""
    coordinator = mock_setup_entry.runtime_data
    mock_droplet.get_availability.return_value = False

    coordinator._on_update(None)

    assert coordinator.lifetime_volume == 0.0
    mock_droplet.get_volume_delta.assert_not_called()


async def test_hourly_boundary_crossing(
    hass: HomeAssistant,
    mock_setup_entry: MockConfigEntry,
    mock_droplet: MagicMock,
) -> None:
    """Test hourly period boundary resets accumulator."""
    coordinator = mock_setup_entry.runtime_data

    # Set accumulated volume for current hour
    coordinator._baseline_hourly = 0.5
    mock_droplet._accumulated_volumes["hourly"] = 500.0  # 0.5 L more

    # Force hour boundary crossing
    coordinator._hourly_reset = dt_util.now() - timedelta(hours=2)
    mock_droplet.get_volume_delta.return_value = 10.0
    coordinator._on_update(None)

    # Hourly baseline should be reset (accumulator was reset by mock side_effect)
    assert coordinator._baseline_hourly == 0.0
    mock_droplet.reset_accumulator.assert_any_call("hourly", mock_droplet.reset_accumulator.call_args_list[0][0][1])
    # Hourly consumption buffer should have the finalized hour
    assert len(coordinator._hourly_consumption) == 1
    assert coordinator._hourly_consumption[0][1] == pytest.approx(1.0)


async def test_daily_boundary_crossing(
    hass: HomeAssistant,
    mock_setup_entry: MockConfigEntry,
    mock_droplet: MagicMock,
) -> None:
    """Test daily period boundary resets accumulator."""
    coordinator = mock_setup_entry.runtime_data

    coordinator._baseline_daily = 4.0
    mock_droplet._accumulated_volumes["daily"] = 1000.0  # 1.0 L

    # Force day boundary
    coordinator._daily_reset = dt_util.now() - timedelta(days=2)
    coordinator._hourly_reset = dt_util.now() - timedelta(hours=2)
    mock_droplet.get_volume_delta.return_value = 100.0
    coordinator._on_update(None)

    assert coordinator._baseline_daily == 0.0
    assert len(coordinator._daily_consumption) == 1
    assert coordinator._daily_consumption[0][1] == pytest.approx(5.0)


async def test_flow_samples_recorded(
    hass: HomeAssistant,
    mock_setup_entry: MockConfigEntry,
    mock_droplet: MagicMock,
) -> None:
    """Test flow samples are recorded on each update."""
    coordinator = mock_setup_entry.runtime_data

    mock_droplet.get_flow_rate.return_value = 1.5
    mock_droplet.get_volume_delta.return_value = 10.0
    coordinator._on_update(None)

    mock_droplet.get_flow_rate.return_value = 2.5
    coordinator._on_update(None)

    assert len(coordinator._flow_samples) == 2
    assert coordinator._flow_samples[0][1] == 1.5
    assert coordinator._flow_samples[1][1] == 2.5


async def test_hourly_flow_stats_tracking(
    hass: HomeAssistant,
    mock_setup_entry: MockConfigEntry,
    mock_droplet: MagicMock,
) -> None:
    """Test hourly max/min flow tracking."""
    coordinator = mock_setup_entry.runtime_data

    mock_droplet.get_volume_delta.return_value = 10.0

    mock_droplet.get_flow_rate.return_value = 1.0
    coordinator._on_update(None)

    mock_droplet.get_flow_rate.return_value = 5.0
    coordinator._on_update(None)

    mock_droplet.get_flow_rate.return_value = 2.0
    coordinator._on_update(None)

    assert coordinator._hourly_max_flow == 5.0
    assert coordinator._hourly_min_flow == 1.0


async def test_cost_calculation_metric(
    hass: HomeAssistant,
    mock_setup_entry: MockConfigEntry,
    mock_droplet: MagicMock,
) -> None:
    """Test cost calculation with metric units."""
    coordinator = mock_setup_entry.runtime_data

    # Set tariff to 5.0 per m³
    hass.config_entries.async_update_entry(
        mock_setup_entry,
        options={**mock_setup_entry.options, "water_tariff": 5.0},
    )

    # Simulate 1000L = 1m³ via baseline
    coordinator._baseline_daily = 1000.0
    assert coordinator.daily_cost == pytest.approx(5.0)


async def test_cost_calculation_zero_tariff(
    hass: HomeAssistant,
    mock_setup_entry: MockConfigEntry,
) -> None:
    """Test cost is zero when tariff is zero."""
    coordinator = mock_setup_entry.runtime_data
    coordinator._baseline_daily = 1000.0
    assert coordinator.daily_cost == 0.0


async def test_statistics_avg_flow_1h(
    hass: HomeAssistant,
    mock_setup_entry: MockConfigEntry,
    mock_droplet: MagicMock,
) -> None:
    """Test average flow 1h computation."""
    coordinator = mock_setup_entry.runtime_data

    # No samples yet
    assert coordinator.avg_flow_1h is None

    # Add samples
    mock_droplet.get_volume_delta.return_value = 10.0
    mock_droplet.get_flow_rate.return_value = 2.0
    coordinator._on_update(None)

    mock_droplet.get_flow_rate.return_value = 4.0
    coordinator._on_update(None)

    assert coordinator.avg_flow_1h == pytest.approx(3.0)


async def test_leak_detection_triggered(
    hass: HomeAssistant,
    mock_setup_entry: MockConfigEntry,
) -> None:
    """Test leak detection triggers when min_flow > threshold."""
    coordinator = mock_setup_entry.runtime_data

    # Set threshold to 0 (default)
    # Set hourly flow stats with min > 0
    now_ts = dt_util.now().timestamp()
    coordinator._hourly_flow_stats = [(now_ts - 3600 * i, 2.0, 0.5) for i in range(24)]

    # Evaluate leak
    coordinator._evaluate_leak()

    assert coordinator.water_leak_detected is True
    assert coordinator.pending_leak_event is not None
    assert coordinator.pending_leak_event[0] == EVENT_WATER_LEAK_DETECTED


async def test_leak_detection_cleared(
    hass: HomeAssistant,
    mock_setup_entry: MockConfigEntry,
) -> None:
    """Test leak detection clears when min_flow <= threshold."""
    coordinator = mock_setup_entry.runtime_data
    coordinator._water_leak_detected = True

    now_ts = dt_util.now().timestamp()
    coordinator._hourly_flow_stats = [(now_ts - 3600 * i, 2.0, 0.0) for i in range(24)]

    coordinator._evaluate_leak()

    assert coordinator.water_leak_detected is False
    assert coordinator.pending_leak_event is not None
    assert coordinator.pending_leak_event[0] == EVENT_WATER_LEAK_CLEARED


async def test_leak_no_change(
    hass: HomeAssistant,
    mock_setup_entry: MockConfigEntry,
) -> None:
    """Test leak detection does nothing when state unchanged."""
    coordinator = mock_setup_entry.runtime_data

    # No flow stats → min_flow is None → no change
    coordinator._evaluate_leak()
    assert coordinator.water_leak_detected is False
    assert coordinator.pending_leak_event is None


async def test_consume_leak_event(
    hass: HomeAssistant,
    mock_setup_entry: MockConfigEntry,
) -> None:
    """Test consuming a pending leak event."""
    coordinator = mock_setup_entry.runtime_data
    coordinator._pending_leak_event = (
        EVENT_WATER_LEAK_DETECTED,
        {"min_flow": 0.5, "threshold": 0.0},
    )

    coordinator.consume_leak_event()
    assert coordinator.pending_leak_event is None


async def test_persistence_save_load(
    hass: HomeAssistant,
    mock_setup_entry: MockConfigEntry,
) -> None:
    """Test data persistence save and load cycle."""
    coordinator = mock_setup_entry.runtime_data

    # Set some baseline data
    coordinator._baseline_lifetime = 8500.5
    coordinator._baseline_daily = 123.4
    coordinator._water_leak_detected = True

    # Save
    await coordinator._async_save_data()

    # Reset values
    coordinator._baseline_lifetime = 0.0
    coordinator._baseline_daily = 0.0
    coordinator._water_leak_detected = False

    # Load
    await coordinator._async_load_data()

    assert coordinator._baseline_lifetime == pytest.approx(8500.5)
    assert coordinator._baseline_daily == pytest.approx(123.4)
    assert coordinator._water_leak_detected is True


async def test_buffer_trimming(
    hass: HomeAssistant,
    mock_setup_entry: MockConfigEntry,
) -> None:
    """Test buffer trimming removes old entries."""
    coordinator = mock_setup_entry.runtime_data
    now_ts = dt_util.now().timestamp()

    # Add old and new flow samples
    coordinator._flow_samples = [
        (now_ts - 7200, 1.0),  # 2h old (should be trimmed)
        (now_ts - 1800, 2.0),  # 30min old (should remain)
    ]

    coordinator._trim_buffers(now_ts)

    assert len(coordinator._flow_samples) == 1
    assert coordinator._flow_samples[0][1] == 2.0


async def test_accumulators_registered_on_setup(
    hass: HomeAssistant,
    mock_setup_entry: MockConfigEntry,
    mock_droplet: MagicMock,
) -> None:
    """Test pydroplet accumulators are registered during setup."""
    registered_names = [
        call[0][0] for call in mock_droplet.add_accumulator.call_args_list
    ]
    assert "hourly" in registered_names
    assert "daily" in registered_names
    assert "weekly" in registered_names
    assert "monthly" in registered_names
    assert "yearly" in registered_names
    assert "lifetime" in registered_names
