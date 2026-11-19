"""EnergyPilot demo page (issue #9, R1 and R2).

Pick an appliance, a run time and a deadline, press Plan, and see the cheapest
start time in the price chart with a short explanation.

Run: streamlit run app.py
"""
import math
from datetime import date, datetime, time, timedelta

import altair as alt
import pandas as pd
import streamlit as st

SLOT = timedelta(minutes=15)
UNIT = "KRW"

# Default run time (minutes) and assumed average power (kW) per appliance.
APPLIANCES = {
    "Washing machine": (120, 0.8),
    "Dryer": (90, 2.0),
    "Dishwasher": (150, 1.0),
}


def temp_prices(day):
    """TEMPORARY made-up prices until the price file (#7) is ready.

    Agreed format: columns start, price (KRW/kWh), one row per 15-minute slot,
    48 hours from midnight of `day` (192 rows). Cheap at night (lowest 03:00-05:00),
    expensive in the morning and evening.
    """
    hourly = [95, 90, 85, 80, 80, 85, 90] + [130, 140, 135] + [115] * 7 + [140, 145, 140, 125, 110] + [100, 95]
    start = datetime.combine(day, time())
    rows = [(start + i * SLOT, hourly[i // 4 % 24]) for i in range(192)]
    return pd.DataFrame(rows, columns=["start", "price"])


def cheapest_start(prices, duration_slots, deadline):
    """TEMPORARY stand-in for the scheduler (#8), with the agreed signature.

    Returns (start, cost) for the cheapest window that ends by `deadline`, or None
    if nothing fits. Cost is for 1 kW: sum of slot prices x 0.25 h.
    """
    best = None
    for i in range(len(prices) - duration_slots + 1):
        if prices["start"].iloc[i] + duration_slots * SLOT > deadline:
            break
        cost = prices["price"].iloc[i:i + duration_slots].sum() * 0.25
        if best is None or cost < best[1]:
            best = (prices["start"].iloc[i], cost)
    return best


st.set_page_config(page_title="EnergyPilot", page_icon="⚡")
st.title("EnergyPilot")
st.caption("Prices are temporary made-up values until the price file is ready.")

today = date.today()
# Plan from the next 15-minute slot, so a start time is never in the past.
earliest = pd.Timestamp.now().ceil("15min")
prices = temp_prices(today)
prices = prices[prices["start"] >= earliest].reset_index(drop=True)

appliance = st.selectbox("Appliance", list(APPLIANCES))
default_minutes, power = APPLIANCES[appliance]
run_minutes = st.number_input("Run time (minutes)", 15, 600, default_minutes, step=15)
st.caption(f"Assumed average power: {power} kW")
day = st.selectbox("Deadline day", [today, today + timedelta(days=1)], index=1,
                   format_func=lambda d: "Today" if d == today else "Tomorrow")
deadline_time = st.time_input("Done by", time(7, 0), step=SLOT)
deadline = datetime.combine(day, deadline_time)

window = None
if st.button("Plan", type="primary"):
    slots = math.ceil(run_minutes / 15)
    result = cheapest_start(prices, slots, deadline)
    if result is None:
        st.error("Nothing fits before the deadline. Pick a later deadline or a shorter run time.")
    else:
        start, cost_1kw = result
        end = start + slots * SLOT
        cost = cost_1kw * power
        first_cost = prices["price"].iloc[:slots].sum() * 0.25 * power
        window = (start, end)
        st.success(f"Starts {start:%H:%M}, costs {cost:.0f} {UNIT}")
        st.write(
            f"The {appliance.lower()} runs {start:%a %H:%M}–{end:%H:%M} and is done before "
            f"{deadline:%a %H:%M}. This is the cheapest {run_minutes}-minute window before the "
            f"deadline. Starting now ({earliest:%H:%M}) would cost {first_cost:.0f} {UNIT}."
        )

chart = alt.Chart(prices).mark_line(interpolate="step-after").encode(
    x=alt.X("start:T", title="Time", axis=alt.Axis(format="%a %H:%M")),  # 24-hour, like "Done by"
    y=alt.Y("price:Q", title=f"Price ({UNIT}/kWh)"),
)
if window:
    shade = alt.Chart(pd.DataFrame({"start": [window[0]], "end": [window[1]]})).mark_rect(
        opacity=0.25, color="green").encode(x="start:T", x2="end:T")
    chart = shade + chart
st.altair_chart(chart)
