"""Helper functions for Droplet."""

from __future__ import annotations

from datetime import datetime, timedelta


def normalize_pairing_code(code: str) -> str:
    """Normalize a pairing code by uppercasing and removing spaces."""
    return code.upper().replace(" ", "")


def is_new_hour(last_reset: datetime, now: datetime) -> bool:
    """Check if the hour boundary has been crossed."""
    return (
        now.year != last_reset.year
        or now.month != last_reset.month
        or now.day != last_reset.day
        or now.hour != last_reset.hour
    )


def is_new_day(last_reset: datetime, now: datetime) -> bool:
    """Check if the day boundary has been crossed."""
    return now.year != last_reset.year or now.month != last_reset.month or now.day != last_reset.day


def is_new_week(last_reset: datetime, now: datetime) -> bool:
    """Check if the ISO week boundary has been crossed."""
    return now.isocalendar().week != last_reset.isocalendar().week or now.year != last_reset.year


def is_new_month(last_reset: datetime, now: datetime) -> bool:
    """Check if the month boundary has been crossed."""
    return now.year != last_reset.year or now.month != last_reset.month


def is_new_year(last_reset: datetime, now: datetime) -> bool:
    """Check if the year boundary has been crossed."""
    return now.year != last_reset.year


def next_hour(now: datetime) -> datetime:
    """Return the start of the next hour."""
    return now.replace(minute=0, second=0, microsecond=0) + timedelta(hours=1)


def next_day(now: datetime) -> datetime:
    """Return the start of the next day."""
    return now.replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)


def next_week(now: datetime) -> datetime:
    """Return the start of the next ISO week (Monday)."""
    days_ahead = 7 - now.weekday()
    return now.replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=days_ahead)


def next_month(now: datetime) -> datetime:
    """Return the start of the next month."""
    if now.month == 12:
        return now.replace(
            year=now.year + 1, month=1, day=1, hour=0, minute=0, second=0, microsecond=0
        )
    return now.replace(month=now.month + 1, day=1, hour=0, minute=0, second=0, microsecond=0)


def next_year(now: datetime) -> datetime:
    """Return the start of the next year."""
    return now.replace(year=now.year + 1, month=1, day=1, hour=0, minute=0, second=0, microsecond=0)


def compute_average(
    samples: list[tuple[float, float]], max_age: float, now_ts: float
) -> float | None:
    """Compute average from timestamped samples within max_age window.

    Args:
        samples: List of (timestamp, value) tuples.
        max_age: Maximum age in seconds for samples to include.
        now_ts: Current timestamp for age calculation.

    Returns:
        Average value or None if no valid samples.

    """
    cutoff = now_ts - max_age
    valid = [v for ts, v in samples if ts >= cutoff]
    if not valid:
        return None
    return sum(valid) / len(valid)


def compute_max(samples: list[tuple[float, float]], max_age: float, now_ts: float) -> float | None:
    """Compute maximum from timestamped samples within max_age window.

    Args:
        samples: List of (timestamp, value) tuples.
        max_age: Maximum age in seconds for samples to include.
        now_ts: Current timestamp for age calculation.

    Returns:
        Maximum value or None if no valid samples.

    """
    cutoff = now_ts - max_age
    valid = [v for ts, v in samples if ts >= cutoff]
    if not valid:
        return None
    return max(valid)


def compute_min(samples: list[tuple[float, float]], max_age: float, now_ts: float) -> float | None:
    """Compute minimum from timestamped samples within max_age window.

    Args:
        samples: List of (timestamp, value) tuples.
        max_age: Maximum age in seconds for samples to include.
        now_ts: Current timestamp for age calculation.

    Returns:
        Minimum value or None if no valid samples.

    """
    cutoff = now_ts - max_age
    valid = [v for ts, v in samples if ts >= cutoff]
    if not valid:
        return None
    return min(valid)
