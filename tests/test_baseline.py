import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).parents[1]))  # so "ai" can be imported when running pytest
from ai.baseline import backtest, same_hour_last_week, same_hour_yesterday, to_15min

# 8 days of hourly prices from 2026-01-01: price = day number * 100 + hour (day 0 = Jan 1)
START = pd.date_range("2026-01-01", periods=8 * 24, freq="h")
PRICES = pd.DataFrame({"start": START, "price": [d * 100 + h for d in range(8) for h in range(24)]})
CUTOFF = pd.Timestamp("2026-01-08")  # day 7


def test_same_hour_yesterday():
    forecast = same_hour_yesterday(PRICES[PRICES["start"] < CUTOFF], CUTOFF)
    assert forecast["start"].tolist() == list(pd.date_range(CUTOFF, periods=24, freq="h"))
    assert forecast["price"].tolist() == [600 + h for h in range(24)]  # day 6


def test_same_hour_last_week():
    forecast = same_hour_last_week(PRICES[PRICES["start"] < CUTOFF], CUTOFF)
    assert forecast["price"].tolist() == list(range(24))  # day 0


def test_backtest_mean_absolute_error():
    # Day 7 is 700 + h: yesterday misses by 100 every hour, last week by 700.
    assert backtest(PRICES, same_hour_yesterday, [CUTOFF]) == 100
    assert backtest(PRICES, same_hour_last_week, [CUTOFF]) == 700


def test_to_15min_repeats_each_hour_four_times():
    slots = to_15min(same_hour_yesterday(PRICES, CUTOFF))
    assert len(slots) == 96
    assert slots["start"].iloc[1] == CUTOFF + pd.Timedelta(minutes=15)
    assert slots["price"].iloc[:5].tolist() == [600, 600, 600, 600, 601]
