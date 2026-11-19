from datetime import date, time

from streamlit.testing.v1 import AppTest


def run_app():
    at = AppTest.from_file("../app.py", default_timeout=30)  # first import is slow
    at.run()
    return at


def test_plans_cheapest_start_at_night():
    at = run_app()  # Washing machine, 120 min, 0.8 kW, done by 07:00 tomorrow
    at.button[0].click().run()
    assert not at.exception
    # Cheapest night hours are 03:00-05:00 at 80 KRW/kWh, and the next night is always
    # ahead of now: 8 slots x 80 x 0.25 h x 0.8 kW = 128 KRW.
    assert at.success[0].value == "Starts 03:00, costs 128 KRW"


def test_shows_error_when_nothing_fits():
    at = run_app()
    at.selectbox[1].set_value(date.today())
    at.time_input[0].set_value(time(0, 30)).run()
    at.button[0].click().run()
    assert not at.exception
    assert len(at.error) == 1
    assert len(at.success) == 0
