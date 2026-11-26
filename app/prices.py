"""Electricity prices for the demo (issue #7, R3).

app/prices.csv holds one made-up day: a price (KRW/kWh) for each 15-minute
slot, cheap at night and expensive in the morning and evening.
"""
from datetime import date
from pathlib import Path

import pandas as pd

PRICE_FILE = Path(__file__).with_name("prices.csv")


def load_prices(day=None):
    """Return 48 hours of prices from midnight of `day` (default: today).

    Columns: start (timestamp) and price (KRW/kWh), one row per 15-minute
    slot, 192 rows. The day in the price file is used twice.
    """
    one_day = pd.read_csv(PRICE_FILE)["price"].tolist()
    start = pd.date_range(pd.Timestamp(day or date.today()), periods=2 * len(one_day), freq="15min")
    return pd.DataFrame({"start": start, "price": one_day * 2})
