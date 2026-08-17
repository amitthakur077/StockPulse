import streamlit as st

# Configure basic page settings before switching
st.set_page_config(
    page_title="StockPulse - Market Analytics",
    page_icon="📈",
    layout="wide"
)

# Instantly redirect the landing page to the main dashboard
st.switch_page("pages/Dashboard.py")
