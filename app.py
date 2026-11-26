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

from app.explanation import explain
from app.prices import load_prices
from app.scheduler import cheapest_start

SLOT = timedelta(minutes=15)
UNIT = "KRW"

# Default run time (minutes) and assumed average power (kW) per appliance.
APPLIANCES = {
    "Washing machine": (120, 0.8),
    "Dryer": (90, 2.0),
    "Dishwasher": (150, 1.0),
}


st.set_page_config(page_title="EnergyPilot", page_icon="⚡")
st.title("EnergyPilot")
st.caption("Prices are made-up example prices (KRW/kWh), so the saving is an estimate, not a real bill.")

today = date.today()
# Plan from the next 15-minute slot, so a start time is never in the past.
earliest = pd.Timestamp.now().ceil("15min")
prices = load_prices(today)
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
        window = (start, end)
        st.success(f"Starts {start:%H:%M}, costs {cost:.0f} {UNIT}")
        st.write(f"{explain(appliance, prices, start, earliest, slots, power)} "
                 f"Done before the deadline, {deadline:%a %H:%M}.")

chart = alt.Chart(prices).mark_line(interpolate="step-after").encode(
    x=alt.X("start:T", title="Time", axis=alt.Axis(format="%a %H:%M")),  # 24-hour, like "Done by"
    y=alt.Y("price:Q", title=f"Price ({UNIT}/kWh)"),
)
if window:
    shade = alt.Chart(pd.DataFrame({"start": [window[0]], "end": [window[1]]})).mark_rect(
        opacity=0.25, color="green").encode(x="start:T", x2="end:T")
    chart = shade + chart
st.altair_chart(chart)
