import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import random

st.title("🛫 Simulated Traffic Management")

# Create state for simulated traffic
if "simulated_traffic" not in st.session_state:
    st.session_state.simulated_traffic = {}

# --- Controls ---
col1, col2 = st.columns(2)
with col1:
    num_drones = st.number_input("Number of Drones to Simulate", 1, 100, 5)
with col2:
    num_wps = st.slider("Waypoints per Drone", 3, 20, 8)

if st.button("➕ Generate Traffic"):
    for i in range(num_drones):
        drone_id = f"SimDrone_{len(st.session_state.simulated_traffic)}"
        x0, y0, z0 = random.uniform(-100, 100), random.uniform(-100, 100), random.uniform(80, 120)
        waypoints = []
        for j in range(num_wps):
            wp = {
                "x": x0 + random.uniform(-50, 50),
                "y": y0 + random.uniform(-50, 50),
                "z": z0 + random.uniform(-10, 10),
                "t": j * random.uniform(5, 12)
            }
            waypoints.append(wp)
        st.session_state.simulated_traffic[drone_id] = waypoints
    st.success(f"✅ {num_drones} drones added!")

# --- Traffic Table View ---
if not st.session_state.simulated_traffic:
    st.warning("No simulated traffic generated yet.")
else:
    st.markdown("---")
    st.subheader("🗂 All Simulated Drones")

    all_data = []
    for drone_id, wps in st.session_state.simulated_traffic.items():
        for i, wp in enumerate(wps):
            all_data.append({**wp, "Drone ID": drone_id, "Index": i})
    df = pd.DataFrame(all_data)
    st.dataframe(df[["Drone ID", "Index", "x", "y", "z", "t"]], use_container_width=True)

    # --- Plot One Drone ---
    st.markdown("---")
    st.subheader("📈 Preview One Drone")

    drone_ids = list(st.session_state.simulated_traffic.keys())
    selected = st.selectbox("Select a Simulated Drone", drone_ids)
    if selected:
        path = st.session_state.simulated_traffic[selected]
        path_df = pd.DataFrame(path)

        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=path_df["x"],
            y=path_df["y"],
            mode='lines+markers',
            name=selected,
            marker=dict(size=6),
            line=dict(width=2)
        ))
        fig.update_layout(
            title=f"Path for {selected}",
            xaxis_title="X (m)",
            yaxis_title="Y (m)",
            height=500
        )
        st.plotly_chart(fig, use_container_width=True)
