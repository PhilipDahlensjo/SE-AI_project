"""Savings report (issue #14, R8).

Compares the cost of a run at the start the agent chose with a baseline: the
same run started at the earliest allowed time, as a resident without the agent
would do. The prices are made-up (or wholesale KPX prices), so the saving is an
estimate, not a real electricity bill.
"""
import pandas as pd

SLOT_HOURS = 0.25  # one 15-minute slot


def run_cost(prices, start, duration_slots, power_kw):
    """Cost (KRW) of running `duration_slots` slots from `start` at `power_kw`."""
    window = prices[prices["start"] >= pd.Timestamp(start)].head(duration_slots)
    if len(window) < duration_slots or window["start"].iloc[0] != pd.Timestamp(start):
        raise ValueError("No prices for the whole run.")
    return float(window["price"].sum() * SLOT_HOURS * power_kw)


def savings(prices, start, earliest, duration_slots, power_kw):
    """Return cost with the agent, baseline cost and saving in % (spec B, R8)."""
    cost = run_cost(prices, start, duration_slots, power_kw)
    base_cost = run_cost(prices, earliest, duration_slots, power_kw)
    saving_pct = 100 * (base_cost - cost) / base_cost if base_cost else 0.0
    return {"cost": cost, "base_cost": base_cost, "saving_pct": saving_pct}
