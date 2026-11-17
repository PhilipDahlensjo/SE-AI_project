"""Tests for the baseline forecast. Run: python -m pytest ai"""
import pandas as pd

from baseline import forecast_next_day, mean_absolute_error


def two_days_of_prices():
    """Day 1 has price = slot number (0..95), day 2 has price 100 everywhere."""
    start = pd.date_range("2026-01-01", periods=2 * 96, freq="15min")
    price = list(range(96)) + [100.0] * 96
    return pd.DataFrame({"start": start, "price": price})


def test_forecast_has_96_slots_for_the_next_day():
    forecast = forecast_next_day(two_days_of_prices(), "2026-01-01")
    assert len(forecast) == 96
    assert forecast["start"].iloc[0] == pd.Timestamp("2026-01-02 00:00")
    assert forecast["start"].iloc[-1] == pd.Timestamp("2026-01-02 23:45")


def test_forecast_repeats_todays_prices():
    forecast = forecast_next_day(two_days_of_prices(), "2026-01-01")
    assert forecast["price"].tolist() == list(range(96))


def test_mean_absolute_error():
    # Forecast for day 2 is 0..95, actual is 100, so the errors are 100..5 and the mean is 52.5.
    assert mean_absolute_error(two_days_of_prices(), ["2026-01-01"]) == 52.5
