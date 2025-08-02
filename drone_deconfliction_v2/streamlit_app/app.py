# app.py

import streamlit as st

st.set_page_config(page_title="UAV Strategic Deconfliction System", layout="wide")

st.markdown(
    """
    <h1 style='text-align: center;'>🚁 UAV Strategic Deconfliction System</h1>
    <p style='text-align: center;'>Ensuring safe drone operations in shared airspace</p>
    """,
    unsafe_allow_html=True
)

st.markdown("---")
st.info("👈 Select a section from the sidebar to begin.")
