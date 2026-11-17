"""Baseline price forecast (R4): tomorrow is like today.

The forecast for the next day repeats today's 96 quarter-hour prices.
Smarter methods are compared against this baseline later.

Run:    python ai/baseline.py
        Prints the mean absolute error over the last 30 days.
"""
from pathlib import Path

import pandas as pd

PRICES = Path(__file__).parent / "data" / "kpx" / "prices_15min.csv"
ONE_DAY = pd.Timedelta(days=1)


def load_prices(path=PRICES):
    """Read the price file: columns start (timestamp) and price (KRW/kWh)."""
    return pd.read_csv(path, parse_dates=["start"])


def forecast_next_day(prices, day):
    """Forecast the prices of the day after `day` by repeating the prices of `day`."""
    day = pd.Timestamp(day).normalize()
    today = prices[(prices["start"] >= day) & (prices["start"] < day + ONE_DAY)]
    return pd.DataFrame({"start": today["start"] + ONE_DAY, "price": today["price"].to_numpy()})


def mean_absolute_error(prices, days):
    """Average absolute difference (KRW/kWh) between forecast and actual price over `days`."""
    actual = prices.set_index("start")["price"]
    errors = []
    for day in days:
        forecast = forecast_next_day(prices, day)
        errors.append(abs(forecast["price"].to_numpy() - actual[forecast["start"]].to_numpy()).mean())
    return sum(errors) / len(errors)


if __name__ == "__main__":
    prices = load_prices()
    last_day = prices["start"].max().normalize()
    days = pd.date_range(last_day - 30 * ONE_DAY, last_day - ONE_DAY)
    mae = mean_absolute_error(prices, days)
    print(f"Baseline 'tomorrow is like today', {len(days)} days up to {last_day.date()}:")
    print(f"  mean absolute error: {mae:.2f} KRW/kWh")
    print(f"  mean price:          {prices[prices['start'] >= days[0] + ONE_DAY]['price'].mean():.2f} KRW/kWh")
