import sys
from pathlib import Path
from unittest.mock import Mock

import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).parents[1]))
from ai import chronos_2
from ai.baseline import backtest, to_15min


def test_chronos_forecast_uses_only_past_prices(monkeypatch):
    hours = pd.date_range("2026-01-01", periods=48, freq="h")
    prices = pd.DataFrame({"start": hours, "price": range(48)})
    cutoff = hours[24]
    pipeline = Mock()
    pipeline.predict_df.return_value = pd.DataFrame(
        {"start": hours[24:], "0.5": range(24, 48), "predictions": -1}
    )
    monkeypatch.setattr(chronos_2, "_load_pipeline", lambda: pipeline)

    forecast = chronos_2.chronos_2(prices, cutoff)

    context, = pipeline.predict_df.call_args.args
    assert context["start"].tolist() == list(hours[:24])
    assert pipeline.predict_df.call_args.kwargs["prediction_length"] == 24
    assert pipeline.predict_df.call_args.kwargs["quantile_levels"] == [0.5]
    pd.testing.assert_frame_equal(forecast, prices.iloc[24:].reset_index(drop=True))
    assert len(to_15min(forecast)) == 96
    assert backtest(prices, chronos_2.chronos_2, [cutoff]) == 0


def test_chronos_rejects_stale_history():
    hours = pd.date_range("2026-01-01", periods=4, freq="h")
    prices = pd.DataFrame({"start": hours[:3], "price": [8, 9, 10]})
    with pytest.raises(ValueError, match="one hour before the cutoff"):
        chronos_2.chronos_2(prices, hours[-1] + pd.Timedelta(hours=1))
