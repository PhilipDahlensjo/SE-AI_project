# EnergyPilot: AI-Based Forecasting for a Proactive Energy-Saving Home

**ITE351 AI & Applications – Group 12 (AI + SE)**

## Contents

- [Group members](#group-members)
- [Research idea](#research-idea)
- [Datasets](#datasets)

## Group members

| Name | Organization | Email |
|---|---|---|
| Filip Kadmark | Hanyang University | filipkadmark@gmail.com |
| Philip Dahlensjoe | Hanyang University | philip.dahlensjo@gmail.com |
| Jasmin Hansson | Hanyang University | jassehansson2014@gmail.com |
| Lucas Roy-Picard | Hanyang University | lucas.roy-picard.1@ens.etsmtl.ca |

## Research idea

**Title:** EnergyPilot: AI-Based Forecasting for a Proactive Energy-Saving Home

**Proposal:**
Electricity prices change during the day, but most households run their washing machine, dryer and dishwasher whenever it suits them, often when power is most expensive. Moving these flexible loads to cheaper hours lowers the bill and eases the load on the grid, but doing it by hand takes effort.

Our idea is part of EnergyPilot, our combined AI + SE project on a proactive agentic home. In the AI part, we want to explore how machine learning can predict electricity prices and a household's energy use for the coming day. Using public price and household consumption data, we will analyze the patterns step by step and compare a few forecasting methods. The predictions can then help decide when appliances should run, and show how much a household could save.

## Datasets

EnergyPilot uses South Korean wholesale electricity prices from the Korea Power Exchange (KPX) and household electricity measurements from France for its next-day forecasts.

| Dataset | Coverage | Fields we plan to use |
|---|---|---|
| [KPX hourly System Marginal Price (SMP), converted to 15-minute slots](https://github.com/PhilipDahlensjo/SE-AI_project/blob/kpx-prices-15min/ai/data/kpx/prices_15min.csv) | South Korea, January 1, 2024 to November 16, 2026, with 100,896 slots | The `start` column gives the beginning of each slot and `price` gives the wholesale SMP in KRW/kWh. |
| [Household Electric Power Consumption](https://www.kaggle.com/datasets/uciml/electric-power-consumption-data-set) | 2,075,259 one-minute records from one household in Sceaux, France, December 2006 to November 2010 | `Date` and `Time` identify each reading. `Global_active_power` gives whole-home active power in kW. `Sub_metering_1` and `Sub_metering_2` give energy in Wh for the kitchen and laundry circuits. Each circuit serves several devices. [Original UCI dataset](https://archive.ics.uci.edu/dataset/235/individual+household+electric+power+consumption) |

For the **price forecast**, we will use wholesale SMP as the target. A conversion script reads the hourly KPX export from EPSIS and copies each hourly value into the four 15-minute slots within that hour. We will train and evaluate at the source's hourly resolution and use the existing 15-minute CSV for the scheduler demo. [KPX conversion script](https://github.com/PhilipDahlensjo/SE-AI_project/blob/kpx-prices-15min/ai/convert_kpx.py)

**Why the scheduler uses 15-minute slots.** The scheduler in the [EnergyPilot specification](EnergyPilot_A_B.pdf) checks appliance start times in quarter-hour steps so it can fit a run around deadlines and quiet hours. A 45-minute wash starting at 15:45 uses the 15:00 hourly rate for its first slot and the 16:00 hourly rate for its next two slots. The scheduler multiplies each slot's rate (KRW/kWh) by the energy used in that slot (power in kW × 0.25 hours), then adds the slot costs. Repeating the hourly rate gives the scheduler a price for every slot while preserving the original price throughout each hour.

For the **household usage forecast**, we will combine `Date` and `Time`, flag hours with incomplete readings, and sum the minute-average active power readings divided by 60 to obtain hourly consumption in kWh. The circuit measurements will help us explore when kitchen and laundry loads are typically active.

The datasets cover different places and years, so we will forecast and evaluate each series separately. The scheduling demo will use the KPX wholesale prices to estimate the cost of simulated appliance runs in KRW. The household data represents a single home, and retail savings would depend on the customer's tariff and appliance use.
