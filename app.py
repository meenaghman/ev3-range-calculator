#! /usr/bin/python3

import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="Kia EV3 Range Planner", page_icon="⚡", layout="centered"
)

TOTAL_BATTERY_KWH = 78.0
SAFETY_FLOOR_PCT = 20.0

st.title("⚡ Kia EV3 Range Planner")

# Sliders for easy touch control
current_pct = st.slider(
    "Current Battery (%)",
    min_value=int(SAFETY_FLOOR_PCT),
    max_value=100,
    value=85,
    step=1,
)

journey_length = st.slider(
    "Target Journey Distance (miles)",
    min_value=10,
    max_value=350,
    value=140,
    step=5,
)

# Core calculations
pct_to_use = current_pct - SAFETY_FLOOR_PCT
usable_kwh = TOTAL_BATTERY_KWH * (pct_to_use / 100.0)
abs_usable_kwh = TOTAL_BATTERY_KWH * (current_pct / 100.0)

# Quick Summary Metrics
st.subheader("Journey Feasibility")
col1, col2 = st.columns(2)
with col1:
    st.metric("Battery to 20% Floor", f"{usable_kwh:.1f} kWh")
with col2:
    st.metric("Total Battery Energy", f"{abs_usable_kwh:.1f} kWh")

# Build efficiency table
efficiencies = [round(x * 0.1, 1) for x in range(20, 36)]
data = []

for m_per_kwh in efficiencies:
    range_to_20 = usable_kwh * m_per_kwh
    range_to_0 = abs_usable_kwh * m_per_kwh
    buffer_left = range_to_20 - journey_length
    can_complete = (
        "✅ Yes"
        if buffer_left >= 0
        else f"❌ Short {abs(round(buffer_left, 1))} mi"
    )

    data.append(
        {
            "Efficiency (mi/kWh)": m_per_kwh,
            "Range to 20%": f"{round(range_to_20, 1)} mi",
            "Range to 0%": f"{round(range_to_0, 1)} mi",
            "Target Achievable (>20%)": can_complete,
            "Buffer at Target": f"{round(buffer_left, 1)} mi",
        }
    )

df = pd.DataFrame(data)

# Interactive Data Table
st.dataframe(df, use_container_width=True, hide_index=True)

# Visual Bar Chart for Range to 20% vs Journey Target
st.subheader("Range to 20% vs Efficiency")
chart_df = pd.DataFrame(
    {
        "Efficiency": [d["Efficiency (mi/kWh)"] for d in data],
        "Range to 20%": [usable_kwh * e for e in efficiencies],
    }
).set_index("Efficiency")

st.bar_chart(chart_df)
st.caption(
    f"Dotted reference line needed for journey: **{journey_length} miles**"
)
