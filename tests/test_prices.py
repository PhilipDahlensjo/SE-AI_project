import sys
from datetime import date
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).parents[1]))  # so "app" can be imported when running pytest
from app.prices import PRICE_FILE, load_prices

DAY = date(2026, 11, 20)


def test_file_has_one_price_per_15_minutes():
    day = pd.read_csv(PRICE_FILE)
    assert len(day) == 96
    assert day["time"].iloc[0] == "00:00" and day["time"].iloc[-1] == "23:45"


def test_48_hours_from_midnight():
    prices = load_prices(DAY)
    assert list(prices.columns) == ["start", "price"]
    assert len(prices) == 192
    assert prices["start"].iloc[0] == pd.Timestamp("2026-11-20 00:00")
    assert prices["start"].iloc[-1] == pd.Timestamp("2026-11-21 23:45")
    assert (prices["start"].diff().dropna() == pd.Timedelta(minutes=15)).all()


def test_second_day_repeats_first_day():
    prices = load_prices(DAY)["price"]
    assert prices.iloc[:96].tolist() == prices.iloc[96:].tolist()


def test_night_is_cheaper_than_evening():
    prices = load_prices(DAY).set_index("start")["price"]
    assert prices["2026-11-20 03:00"] < prices["2026-11-20 18:00"]


def test_default_day_is_today():
    assert load_prices()["start"].iloc[0] == pd.Timestamp(date.today())
