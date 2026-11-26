import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).parents[1]))  # so "app" can be imported when running pytest
from app.scheduler import cheapest_start

# 8 slots from midnight, cheap at 00:30-01:00
PRICES = pd.DataFrame({
    "start": pd.date_range("2026-11-20 00:00", periods=8, freq="15min"),
    "price": [100, 100, 50, 50, 100, 100, 100, 100],
})


def test_picks_the_cheap_window():
    start, cost = cheapest_start(PRICES, 2, "2026-11-20 02:00")
    assert start == pd.Timestamp("2026-11-20 00:30")
    assert cost == 25.0  # (50 + 50) x 0.25 h


def test_deadline_cuts_off_the_cheap_window():
    # the cheap window ends 01:00, too late, so the best is 00:15-00:45 which ends right at the deadline
    start, cost = cheapest_start(PRICES, 2, "2026-11-20 00:45")
    assert start == pd.Timestamp("2026-11-20 00:15")
    assert cost == 37.5  # (100 + 50) x 0.25 h


def test_none_when_nothing_fits():
    assert cheapest_start(PRICES, 2, "2026-11-20 00:15") is None


def test_earliest_wins_on_a_tie():
    flat = PRICES.assign(price=100)
    start, _ = cheapest_start(flat, 2, "2026-11-20 02:00")
    assert start == pd.Timestamp("2026-11-20 00:00")
