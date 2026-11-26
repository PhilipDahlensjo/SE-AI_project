"""Scheduler for the demo (issue #8, R5).

Finds the cheapest start time for an appliance run that is done by the deadline.
"""
from datetime import timedelta

import pandas as pd

SLOT = timedelta(minutes=15)
SLOT_HOURS = 0.25


def cheapest_start(prices, duration_slots, deadline):
    """Return (start, cost) for the cheapest run that ends by `deadline`, or None.

    `prices` is the shared price table (columns start, price, 15-minute slots,
    sorted by time). The cost is for 1 kW, so the caller multiplies by the
    appliance's power.
    """
    deadline = pd.Timestamp(deadline)
    best = None
    for i in range(len(prices) - duration_slots + 1):
        start = prices["start"].iloc[i]
        # prices are sorted, so once one start is too late all the rest are too
        if start + duration_slots * SLOT > deadline:
            break
        cost = float(prices["price"].iloc[i:i + duration_slots].sum() * SLOT_HOURS)
        # strict < so the earlier start wins if two cost the same
        if best is None or cost < best[1]:
            best = (start, cost)
    return best
