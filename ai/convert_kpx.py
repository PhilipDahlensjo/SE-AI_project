"""Convert the KPX hourly SMP Excel export (EPSIS) to a 15-minute price file.

Input:  ai/data/kpx/HOME_전력거래_계통한계가격_시간별SMP.xlsx
        One row per day, columns 01시..24시. KPX labels each hour by its END,
        so 01시 is 00:00-01:00.
Output: ai/data/kpx/prices_15min.csv with columns start, price (KRW/kWh),
        one row per 15-minute slot, oldest first. Each hourly price is used
        for the four slots in that hour.

Run:    python ai/convert_kpx.py
"""
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path

import pandas as pd

DATA = Path(__file__).parent / "data" / "kpx"
SRC = DATA / "HOME_전력거래_계통한계가격_시간별SMP.xlsx"
OUT = DATA / "prices_15min.csv"
NS = {"x": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}


def read_sheet(path):
    """Return the first sheet as a list of rows (lists of strings)."""
    with zipfile.ZipFile(path) as z:
        shared = ["".join(t.text or "" for t in si.iterfind(".//x:t", NS))
                  for si in ET.fromstring(z.read("xl/sharedStrings.xml")).iterfind("x:si", NS)]
        sheet = ET.fromstring(z.read("xl/worksheets/sheet1.xml"))
    rows = []
    for row in sheet.iterfind(".//x:row", NS):
        cells = []
        for c in row.iterfind("x:c", NS):
            v = c.findtext("x:v", "", NS)
            cells.append(shared[int(v)] if c.get("t") == "s" else v)
        rows.append(cells)
    return rows


rows = read_sheet(SRC)
header, body = rows[0], rows[1:]
hours = [h for h in header if h.endswith("시")]  # 01시..24시, drops max/min/average
wide = pd.DataFrame(body, columns=header)[["기간"] + hours]

long = wide.melt(id_vars="기간", var_name="hour", value_name="price")
hour_start = pd.to_datetime(long["기간"], format="%Y/%m/%d") + pd.to_timedelta(
    long["hour"].str[:2].astype(int) - 1, unit="h")
long = pd.DataFrame({"start": hour_start, "price": long["price"].astype(float)})

slots = pd.concat([long.assign(start=long["start"] + pd.Timedelta(minutes=m)) for m in (0, 15, 30, 45)])
slots = slots.sort_values("start").reset_index(drop=True)
slots.to_csv(OUT, index=False, date_format="%Y-%m-%d %H:%M")
print(f"Wrote {len(slots)} rows to {OUT}")
