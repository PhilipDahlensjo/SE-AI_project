import sys
from pathlib import Path

import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).parents[1]))  # so "app" can be imported when running pytest
from app.report import savings

# 8 slots from midnight: expensive, cheap, then expensive again
PRICES = pd.DataFrame({
    "start": pd.date_range("2026-11-20 00:00", periods=8, freq="15min"),
    "price": [100, 100, 50, 50, 100, 100, 100, 100],
})


def test_saving_against_earliest_start():
    result = savings(PRICES, "2026-11-20 00:30", "2026-11-20 00:00", 2, 1.0)
    assert result["cost"] == 25.0  # (50 + 50) x 0.25 h x 1 kW
    assert result["base_cost"] == 50.0  # (100 + 100) x 0.25 h x 1 kW
    assert result["saving_pct"] == 50.0


def test_power_scales_cost_but_not_percent():
    result = savings(PRICES, "2026-11-20 00:30", "2026-11-20 00:00", 2, 2.0)
    assert result["cost"] == 50.0
    assert result["base_cost"] == 100.0
    assert result["saving_pct"] == 50.0


def test_no_saving_when_agent_starts_at_earliest():
    result = savings(PRICES, "2026-11-20 00:00", "2026-11-20 00:00", 2, 1.0)
    assert result["saving_pct"] == 0.0


def test_error_when_run_does_not_fit():
    with pytest.raises(ValueError):
        savings(PRICES, "2026-11-20 01:45", "2026-11-20 00:00", 2, 1.0)  # only 1 slot left
