"""Explanation of a planned run (R6).

Turns the scheduler's result into a short sentence for the user. All numbers
come from savings() in report.py, so the text can't show a wrong number.
"""
from datetime import timedelta

import pandas as pd

from app.report import savings

SLOT = timedelta(minutes=15)
UNIT = "KRW"


def explain(appliance, prices, start, earliest, duration_slots, power_kw):
    """Return a sentence like "Washing machine runs 03:00-05:00, 38 % cheaper than starting at 20:00 (...)"."""
    start = pd.Timestamp(start)
    earliest = pd.Timestamp(earliest)
    end = start + duration_slots * SLOT
    s = savings(prices, start, earliest, duration_slots, power_kw)

    # if the agent didn't move the run there is no saving to brag about
    if s["saving_pct"] <= 0:
        return (f"{appliance} runs {start:%H:%M}–{end:%H:%M}. Starting at {earliest:%H:%M} "
                f"is already the cheapest time ({s['cost']:.0f} {UNIT}).")

    return (f"{appliance} runs {start:%H:%M}–{end:%H:%M}, {s['saving_pct']:.0f} % cheaper than "
            f"starting at {earliest:%H:%M} ({s['cost']:.0f} instead of {s['base_cost']:.0f} {UNIT}).")
