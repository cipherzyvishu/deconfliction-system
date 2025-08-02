import streamlit as st
import requests
import plotly.graph_objects as go
import pandas as pd

st.title("📊 Mission Analysis Results")

# Check data availability
if "simulated_traffic" not in st.session_state or not st.session_state.simulated_traffic:
    st.warning("❌ No simulated traffic found. Please generate in previous tab.")
    st.stop()

if "x" not in st.session_state:
    st.warning("❌ No primary mission defined.")
    st.stop()

# Prepare request payload
primary_mission = {
    "waypoints": st.session_state["x"],  # from mission planning page
    "buffer": st.session_state.get("buffer", 20)
}
simulated = st.session_state.simulated_traffic

# Send request to backend
with st.spinner("Analyzing mission..."):
    try:
        res = requests.post("http://127.0.0.1:8000/analyze", json={
            "mission": primary_mission,
            "simulated_drones": simulated
        })
        res.raise_for_status()
        output = res.json()
    except Exception as e:
        st.error(f"Error contacting backend: {e}")
        st.stop()

# Show result
st.success(f"🟢 Status: {output['status'].upper()}")
if output["conflicts"]:
    st.write(f"🚨 Total Conflicts: {len(output['conflicts'])}")
    st.dataframe(pd.DataFrame(output["conflicts"]))
else:
    st.info("✅ No conflicts detected.")

# 3D Plot
st.subheader("🛰️ 3D Conflict Scene")

fig = go.Figure()

# Primary path
wp_df = pd.DataFrame(primary_mission["waypoints"])
fig.add_trace(go.Scatter3d(
    x=wp_df["x"], y=wp_df["y"], z=wp_df["z"],
    mode='lines+markers',
    line=dict(color="blue"),
    name="Primary"
))

# Simulated drones
for drone_id, wps in simulated.items():
    df = pd.DataFrame(wps)
    fig.add_trace(go.Scatter3d(
        x=df["x"], y=df["y"], z=df["z"],
        mode='lines+markers',
        line=dict(width=1),
        name=drone_id
    ))

# Conflict points
for c in output["conflicts"]:
    fig.add_trace(go.Scatter3d(
        x=[c["location"][0]], y=[c["location"][1]], z=[c["location"][2]],
        mode='markers+text',
        marker=dict(color='red', size=6),
        name=f"Conflict w/ {c['with']}",
        text=[f"t={c['time']:.1f}s"],
        textposition="top center"
    ))

fig.update_layout(
    height=700,
    scene=dict(
        xaxis_title="X",
        yaxis_title="Y",
        zaxis_title="Z",
    )
)
st.plotly_chart(fig, use_container_width=True)
