"""Tests for Droplet helper functions."""

from __future__ import annotations

from datetime import UTC, datetime

import pytest

from custom_components.droplet.helpers import (
    compute_average,
    compute_max,
    compute_min,
    is_new_day,
    is_new_hour,
    is_new_month,
    is_new_week,
    is_new_year,
    next_day,
    next_hour,
    next_month,
    next_week,
    next_year,
    normalize_pairing_code,
)


class TestNormalizePairingCode:
    """Tests for normalize_pairing_code."""

    def test_uppercase(self) -> None:
        """Test lowercase letters are uppercased."""
        assert normalize_pairing_code("abcd1234") == "ABCD1234"

    def test_remove_spaces(self) -> None:
        """Test spaces are removed."""
        assert normalize_pairing_code("AB CD 12 34") == "ABCD1234"

    def test_already_normalized(self) -> None:
        """Test already normalized code passes through."""
        assert normalize_pairing_code("ABCD1234") == "ABCD1234"

    def test_mixed(self) -> None:
        """Test mixed case with spaces."""
        assert normalize_pairing_code("aB cD 12") == "ABCD12"


class TestPeriodBoundaries:
    """Tests for period boundary detection."""

    def test_is_new_hour_same(self) -> None:
        """Test same hour returns False."""
        last = datetime(2024, 1, 15, 10, 30, tzinfo=UTC)
        now = datetime(2024, 1, 15, 10, 45, tzinfo=UTC)
        assert is_new_hour(last, now) is False

    def test_is_new_hour_different(self) -> None:
        """Test different hour returns True."""
        last = datetime(2024, 1, 15, 10, 59, tzinfo=UTC)
        now = datetime(2024, 1, 15, 11, 0, tzinfo=UTC)
        assert is_new_hour(last, now) is True

    def test_is_new_day_same(self) -> None:
        """Test same day returns False."""
        last = datetime(2024, 1, 15, 10, 0, tzinfo=UTC)
        now = datetime(2024, 1, 15, 23, 59, tzinfo=UTC)
        assert is_new_day(last, now) is False

    def test_is_new_day_different(self) -> None:
        """Test different day returns True."""
        last = datetime(2024, 1, 15, 23, 59, tzinfo=UTC)
        now = datetime(2024, 1, 16, 0, 0, tzinfo=UTC)
        assert is_new_day(last, now) is True

    def test_is_new_week_same(self) -> None:
        """Test same ISO week returns False."""
        last = datetime(2024, 1, 15, tzinfo=UTC)  # Monday, week 3
        now = datetime(2024, 1, 21, tzinfo=UTC)  # Sunday, week 3
        assert is_new_week(last, now) is False

    def test_is_new_week_different(self) -> None:
        """Test different ISO week returns True."""
        last = datetime(2024, 1, 21, tzinfo=UTC)  # Sunday, week 3
        now = datetime(2024, 1, 22, tzinfo=UTC)  # Monday, week 4
        assert is_new_week(last, now) is True

    def test_is_new_month_same(self) -> None:
        """Test same month returns False."""
        last = datetime(2024, 1, 1, tzinfo=UTC)
        now = datetime(2024, 1, 31, tzinfo=UTC)
        assert is_new_month(last, now) is False

    def test_is_new_month_different(self) -> None:
        """Test different month returns True."""
        last = datetime(2024, 1, 31, tzinfo=UTC)
        now = datetime(2024, 2, 1, tzinfo=UTC)
        assert is_new_month(last, now) is True

    def test_is_new_year_same(self) -> None:
        """Test same year returns False."""
        last = datetime(2024, 1, 1, tzinfo=UTC)
        now = datetime(2024, 12, 31, tzinfo=UTC)
        assert is_new_year(last, now) is False

    def test_is_new_year_different(self) -> None:
        """Test different year returns True."""
        last = datetime(2024, 12, 31, tzinfo=UTC)
        now = datetime(2025, 1, 1, tzinfo=UTC)
        assert is_new_year(last, now) is True

    def test_is_new_hour_year_crossing(self) -> None:
        """Test hour boundary across year change."""
        last = datetime(2024, 12, 31, 23, 30, tzinfo=UTC)
        now = datetime(2025, 1, 1, 0, 0, tzinfo=UTC)
        assert is_new_hour(last, now) is True


class TestStatisticsComputation:
    """Tests for statistics computation functions."""

    def test_compute_average_basic(self) -> None:
        """Test basic average computation."""
        samples = [(100.0, 1.0), (200.0, 3.0), (300.0, 5.0)]
        result = compute_average(samples, 500, 400.0)
        assert result == pytest.approx(3.0)

    def test_compute_average_with_expired(self) -> None:
        """Test average ignores expired samples."""
        samples = [(50.0, 10.0), (200.0, 2.0), (300.0, 4.0)]
        result = compute_average(samples, 200, 350.0)
        assert result == pytest.approx(3.0)

    def test_compute_average_empty(self) -> None:
        """Test average returns None for no valid samples."""
        samples = [(100.0, 5.0)]
        result = compute_average(samples, 10, 200.0)
        assert result is None

    def test_compute_average_all_expired(self) -> None:
        """Test average returns None when all samples expired."""
        result = compute_average([], 100, 200.0)
        assert result is None

    def test_compute_max_basic(self) -> None:
        """Test basic max computation."""
        samples = [(100.0, 1.0), (200.0, 5.0), (300.0, 3.0)]
        result = compute_max(samples, 500, 400.0)
        assert result == pytest.approx(5.0)

    def test_compute_max_empty(self) -> None:
        """Test max returns None for no valid samples."""
        result = compute_max([], 100, 200.0)
        assert result is None

    def test_compute_min_basic(self) -> None:
        """Test basic min computation."""
        samples = [(100.0, 3.0), (200.0, 1.0), (300.0, 5.0)]
        result = compute_min(samples, 500, 400.0)
        assert result == pytest.approx(1.0)

    def test_compute_min_empty(self) -> None:
        """Test min returns None for no valid samples."""
        result = compute_min([], 100, 200.0)
        assert result is None

    def test_compute_min_with_expired(self) -> None:
        """Test min ignores expired samples."""
        samples = [(50.0, 0.1), (200.0, 2.0), (300.0, 3.0)]
        result = compute_min(samples, 200, 350.0)
        assert result == pytest.approx(2.0)


class TestNextBoundary:
    """Tests for next period boundary functions."""

    def test_next_hour(self) -> None:
        """Test next_hour returns start of next hour."""
        now = datetime(2024, 1, 15, 10, 30, 45, tzinfo=UTC)
        result = next_hour(now)
        assert result == datetime(2024, 1, 15, 11, 0, 0, tzinfo=UTC)

    def test_next_hour_end_of_day(self) -> None:
        """Test next_hour at end of day crosses to next day."""
        now = datetime(2024, 1, 15, 23, 45, tzinfo=UTC)
        result = next_hour(now)
        assert result == datetime(2024, 1, 16, 0, 0, 0, tzinfo=UTC)

    def test_next_day(self) -> None:
        """Test next_day returns start of next day."""
        now = datetime(2024, 1, 15, 10, 30, tzinfo=UTC)
        result = next_day(now)
        assert result == datetime(2024, 1, 16, 0, 0, 0, tzinfo=UTC)

    def test_next_day_end_of_month(self) -> None:
        """Test next_day at end of month crosses to next month."""
        now = datetime(2024, 1, 31, 23, 59, tzinfo=UTC)
        result = next_day(now)
        assert result == datetime(2024, 2, 1, 0, 0, 0, tzinfo=UTC)

    def test_next_week_monday(self) -> None:
        """Test next_week from Monday returns next Monday."""
        now = datetime(2024, 1, 15, 10, 0, tzinfo=UTC)  # Monday
        result = next_week(now)
        assert result == datetime(2024, 1, 22, 0, 0, 0, tzinfo=UTC)
        assert result.weekday() == 0  # Monday

    def test_next_week_friday(self) -> None:
        """Test next_week from Friday returns next Monday."""
        now = datetime(2024, 1, 19, 14, 0, tzinfo=UTC)  # Friday
        result = next_week(now)
        assert result == datetime(2024, 1, 22, 0, 0, 0, tzinfo=UTC)
        assert result.weekday() == 0  # Monday

    def test_next_month(self) -> None:
        """Test next_month returns start of next month."""
        now = datetime(2024, 1, 15, 10, 0, tzinfo=UTC)
        result = next_month(now)
        assert result == datetime(2024, 2, 1, 0, 0, 0, tzinfo=UTC)

    def test_next_month_december(self) -> None:
        """Test next_month from December crosses to January."""
        now = datetime(2024, 12, 15, tzinfo=UTC)
        result = next_month(now)
        assert result == datetime(2025, 1, 1, 0, 0, 0, tzinfo=UTC)

    def test_next_year(self) -> None:
        """Test next_year returns start of next year."""
        now = datetime(2024, 6, 15, tzinfo=UTC)
        result = next_year(now)
        assert result == datetime(2025, 1, 1, 0, 0, 0, tzinfo=UTC)
