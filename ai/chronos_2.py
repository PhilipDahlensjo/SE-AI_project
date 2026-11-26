"""Next-day KPX price forecasts using the pretrained Amazon Chronos-2 model.

Install with ``python -m pip install "chronos-forecasting>=2.0" pandas``.
Compare against the seasonal baselines with ``python -m ai.chronos_2``.
"""
from functools import cache

import pandas as pd

from .baseline import DAY, HOUR, backtest, load_hourly_prices, same_hour_last_week, same_hour_yesterday


@cache
def _load_pipeline():
    from chronos import Chronos2Pipeline

    return Chronos2Pipeline.from_pretrained("amazon/chronos-2", device_map="cpu")


def chronos_2(history, cutoff):
    """Forecast 24 median hourly prices from cutoff for backtest() or to_15min()."""
    cutoff = pd.Timestamp(cutoff)
    context = history.loc[history["start"] < cutoff, ["start", "price"]].sort_values("start")
    if len(context) < 3 or context["start"].iloc[-1] != cutoff - HOUR:
        raise ValueError("Chronos-2 needs at least three hourly prices ending one hour before the cutoff.")
    if not context["start"].diff().iloc[1:].eq(HOUR).all():
        raise ValueError("Chronos-2 needs regularly spaced hourly prices.")

    forecast = _load_pipeline().predict_df(
        context.assign(item_id="kpx"),
        timestamp_column="start",
        target="price",
        prediction_length=24,
        quantile_levels=[0.5],
    )
    return forecast[["start", "0.5"]].rename(columns={"0.5": "price"})


if __name__ == "__main__":
    prices = load_hourly_prices()
    last_cutoff = prices["start"].max().normalize()
    cutoffs = pd.date_range(last_cutoff - 6 * DAY, last_cutoff)
    print(f"Backtest, {len(cutoffs)} daily cutoffs {cutoffs[0].date()} to {cutoffs[-1].date()}:")
    for method in (same_hour_yesterday, same_hour_last_week, chronos_2):
        print(f"  {method.__name__:20} MAE {backtest(prices, method, cutoffs):6.2f} KRW/kWh")
