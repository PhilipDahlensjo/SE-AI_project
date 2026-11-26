"""Baseline price forecasts (R4), the methods Chronos-2 is compared with.

Two seasonal naive baselines forecast the next 24 hourly prices:
- same hour yesterday: repeat the 24 prices before the cutoff
- same hour last week: repeat the 24 prices that started 7 days before the cutoff

Forecasts are hourly, as in the KPX source. to_15min() repeats each hour in its
four quarter-hour slots for the scheduler.

Run:    python ai/baseline.py
        Backtests both baselines on the last 7 days (one cutoff per midnight)
        and prints the mean absolute error in KRW/kWh.
"""
from pathlib import Path

import pandas as pd

PRICES = Path(__file__).parent / "data" / "kpx" / "prices_15min.csv"
HOUR = pd.Timedelta(hours=1)
DAY = pd.Timedelta(days=1)


def load_hourly_prices(path=PRICES):
    """Hourly prices (start, price in KRW/kWh): one row per hour from the 15-minute file."""
    prices = pd.read_csv(path, parse_dates=["start"])
    return prices[prices["start"].dt.minute == 0].reset_index(drop=True)


def _repeat(history, cutoff, lag):
    """Forecast the 24 hours from `cutoff` with the prices `lag` earlier."""
    cutoff = pd.Timestamp(cutoff)
    hours = pd.date_range(cutoff, periods=24, freq="h")
    past = history.set_index("start")["price"]
    return pd.DataFrame({"start": hours, "price": past[hours - lag].to_numpy()})


def same_hour_yesterday(history, cutoff):
    return _repeat(history, cutoff, DAY)


def same_hour_last_week(history, cutoff):
    return _repeat(history, cutoff, 7 * DAY)


def to_15min(forecast):
    """Repeat each hourly price in its four 15-minute slots (start, price)."""
    return pd.concat(
        [forecast.assign(start=forecast["start"] + pd.Timedelta(minutes=m)) for m in (0, 15, 30, 45)]
    ).sort_values("start").reset_index(drop=True)


def backtest(history, method, cutoffs):
    """Mean absolute error (KRW/kWh) of `method` over the 24 hours after each cutoff.

    The method only sees prices before the cutoff.
    """
    actual = history.set_index("start")["price"]
    errors = []
    for cutoff in cutoffs:
        forecast = method(history[history["start"] < cutoff], cutoff)
        errors.append(abs(forecast["price"].to_numpy() - actual[forecast["start"]].to_numpy()).mean())
    return sum(errors) / len(errors)


if __name__ == "__main__":
    prices = load_hourly_prices()
    last_cutoff = prices["start"].max().normalize()  # last day with all 24 hours
    cutoffs = pd.date_range(last_cutoff - 6 * DAY, last_cutoff)
    print(f"Backtest, {len(cutoffs)} daily cutoffs {cutoffs[0].date()} to {cutoffs[-1].date()}:")
    for method in (same_hour_yesterday, same_hour_last_week):
        print(f"  {method.__name__:20} MAE {backtest(prices, method, cutoffs):6.2f} KRW/kWh")
    print(f"  mean price {prices[prices['start'] >= cutoffs[0]]['price'].mean():.2f} KRW/kWh")
