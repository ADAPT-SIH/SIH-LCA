# app.py
# Streamlit prototype: AI-Driven LCA Tool (India-centric) -- MINIMAL, no matplotlib, no fpdf

import streamlit as st
import pandas as pd

st.set_page_config(page_title="SustainaMine - LCA for Metals", layout="wide")

# ---------------------------
# Helper / metadata (sources)
# ---------------------------
SOURCES = {
    "CPCB_RedMud_Guidelines": "https://cpcb.nic.in/uploads/hwmd/Guidelines_HW_6.pdf",
    "Hazardous_Waste_Rules_2016": "https://www.npcindia.gov.in/NPC/Files/delhiOFC/EM/Hazardous-waste-management-rules-2016.pdf",
    "Minerals_Aluminium_page": "https://mines.gov.in/webportal/content/Aluminium",
    "RedMud_Brochure_JNARDDC": "https://www.jnarddc.gov.in/Files/Red_Mud_Brochure.pdf",
    "Indian_Minerals_Yearbook_Copper": "https://ibm.gov.in/writereaddata/files/1715685346664347e2b0816Copper_2022.pdf",
    "CPCB_Technical_Guidelines": "https://cpcb.nic.in/technical-guidelines/"
}

# ---------------------------
# Informational / context data
# ---------------------------
st.title("SustainaMine — AI-Driven LCA for Metals (India)")
st.markdown("""
**Purpose:** Demonstration prototype for Smart India Hackathon — an AI-assisted Life Cycle Assessment (LCA)
tool tailored for **Aluminium** and **Copper** with circularity, by-product valorization, and regulatory
compliance support for India.

**Note:** Default numbers are *illustrative*. Replace with validated local data for final deployment.
""")

# ---------------------------
# Default lifecycle factors (illustrative)
# ---------------------------
default_factors = {
    "aluminium_virgin_kgco2_per_kg": 16.0,
    "aluminium_recycled_kgco2_per_kg": 4.0,
    "copper_virgin_kgco2_per_kg": 8.0,
    "copper_recycled_kgco2_per_kg": 2.0,
    "red_mud_t_per_t_aluminium": 1.5,
    "so2_kg_per_t_copper": 25.0,
    "transport_kgco2_per_tkm": 0.05,
    "recycle_cost_usd_per_t_aluminium": 200.0,
    "recycle_cost_usd_per_t_copper": 300.0
}

# ---------------------------
# Input panel
# ---------------------------
st.header("Run an LCA Estimate (Demo Input)")

with st.form(key='input_form'):
    col1, col2 = st.columns(2)

    with col1:
        metal = st.selectbox("Select metal", ["Aluminium", "Copper"])
        production_route = st.selectbox("Production route", ["Virgin/Raw", "Recycled", "Mixed"])
        recycled_pct = st.slider("Recycled content (%)", 0, 100, 30)
        ore_quality = st.selectbox("Ore quality", ["High", "Medium", "Low"])

    with col2:
        energy_source = st.selectbox("Energy source", ["Coal-based grid", "Mixed grid", "Renewable-heavy"])
        transport_km = st.number_input("Transport distance (km)", min_value=0, max_value=5000, value=200)
        transport_tonnes = st.number_input("Transport quantity (tonnes)", min_value=1, max_value=10000, value=1)
        eol_option = st.selectbox("End-of-life option", ["Landfill", "Recycling", "Reuse"])

    run_button = st.form_submit_button("Run LCA estimate")

# ---------------------------
# Calculation &
