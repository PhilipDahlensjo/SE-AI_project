import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).parents[1]))  # so "app" can be imported when running pytest
from app.explanation import explain

# same 8 slots as in test_report.py, cheap at 00:30-01:00
PRICES = pd.DataFrame({
    "start": pd.date_range("2026-11-20 00:00", periods=8, freq="15min"),
    "price": [100, 100, 50, 50, 100, 100, 100, 100],
})


def test_text_with_saving():
    text = explain("Washing machine", PRICES, "2026-11-20 00:30", "2026-11-20 00:00", 2, 1.0)
    assert text == ("Washing machine runs 00:30–01:00, 50 % cheaper than starting at 00:00 "
                    "(25 instead of 50 KRW).")


def test_text_when_earliest_is_cheapest():
    text = explain("Dryer", PRICES, "2026-11-20 00:30", "2026-11-20 00:30", 2, 2.0)
    assert text == "Dryer runs 00:30–01:00. Starting at 00:30 is already the cheapest time (50 KRW)."


def test_power_changes_cost_but_not_percent():
    text = explain("Dryer", PRICES, "2026-11-20 00:30", "2026-11-20 00:00", 2, 2.0)
    assert "50 % cheaper" in text
    assert "(50 instead of 100 KRW)" in text
