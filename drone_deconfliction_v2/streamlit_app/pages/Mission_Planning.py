import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, time


st.title("🚁 Primary Mission Planning")

st.subheader("🧭 Configure Primary Mission")

# --- Time Window ---
col1, col2 = st.columns(2)
with col1:
    start_time = st.time_input("Mission Start Time", value=time(10, 0))
with col2:
    end_time = st.time_input("Mission End Time", value=time(10, 30))

# --- Safety Buffer ---
buffer = st.slider("Safety Buffer (meters)", min_value=5, max_value=50, value=20, step=1)

st.markdown("---")
st.subheader("🖊 Define Waypoints")

# --- Waypoint Editor ---
default_wps = pd.DataFrame({
    "x": [0, 50, 100],
    "y": [0, 40, 80],
    "z": [100, 105, 110],
    "t": [0, 10, 20]
})
waypoint_df = st.data_editor(default_wps, num_rows="dynamic", use_container_width=True)

# After editing waypoint_df
st.session_state["x"] = waypoint_df.to_dict("records")
st.session_state["buffer"] = buffer

# --- Preview Path ---
st.markdown("---")
st.subheader("📈 Preview Trajectory")

if not waypoint_df.empty:
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=waypoint_df["x"],
        y=waypoint_df["y"],
        mode='lines+markers',
        marker=dict(size=8, color="blue"),
        line=dict(color="lightblue", width=2),
        name="Drone Path"
    ))
    fig.update_layout(
        xaxis_title="X (m)",
        yaxis_title="Y (m)",
        title="2D Mission Path",
        height=500
    )
    st.plotly_chart(fig, use_container_width=True)
else:
    st.warning("Please input at least 2 waypoints to preview.")

