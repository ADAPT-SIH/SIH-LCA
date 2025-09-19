# app.py
# Streamlit prototype: AI-Driven LCA Tool (India-centric) -- NO matplotlib version

import streamlit as st
import pandas as pd
from fpdf import FPDF

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

st.info("""
**Pro-government framing:** This tool is built to _support_ Government of India objectives — it helps industry
adhere to CPCB / MoEFCC guidelines, follow the Hazardous & Other Wastes Rules (2016), and advance circularity
aligned with National Mineral Policy goals. It **does not** replace statutory approvals — it **assists** compliance.
""")

# ---------------------------
# India context (states + production)
# ---------------------------
st.header("India Context & Production (quick snapshot)")

col1, col2 = st.columns([2, 3])
with col1:
    st.subheader("Major Aluminium-producing states (India)")
    st.write("""
    **Odisha, Gujarat, Maharashtra, Chhattisgarh, Jharkhand**  
    These states host large alumina/aluminium complexes (NALCO, Hindalco, Vedanta, BALCO).
    """)
    st.write("Source links:")
    st.write(f"- CPCB / Guidelines: {SOURCES['CPCB_RedMud_Guidelines']}")
    st.write(f"- Ministry of Mines info: {SOURCES['Minerals_Aluminium_page']}")

with col2:
    st.subheader("Major Copper-producing regions (India)")
    st.write("""
    Copper ore/concentrate and refined copper production has strong footprints in **Rajasthan, Madhya Pradesh**  
    and several large smelter/plant clusters. India imports a large share of concentrates.
    """)
    st.write(f"- Copper Yearbook (IBM): {SOURCES['Indian_Minerals_Yearbook_Copper']}")

st.markdown("---")

# ---------------------------
# Default lifecycle factors (illustrative)
# ---------------------------
st.header("Default LCA parameters (illustrative defaults)")

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

st.json(default_factors)
st.markdown("---")

# ---------------------------
# Input panel
# ---------------------------
st.header("Run an LCA Estimate (Demo Input)")

with st.form(key='input_form'):
    col1, col2, col3 = st.columns(3)

    with col1:
        metal = st.selectbox("Select metal", ["Aluminium", "Copper"])

        if metal == "Aluminium":
            state = st.selectbox("State of extraction",
                                 ["Odisha", "Gujarat", "Maharashtra", "Chhattisgarh", "Jharkhand", "Other"])
            ore_quality = st.selectbox("Bauxite quality", ["High (>45%)", "Medium (35–45%)", "Low (<35%)"])
        else:
            state = st.selectbox("State of extraction",
                                 ["Rajasthan", "Madhya Pradesh", "Jharkhand", "Other/Import"])
            ore_quality = st.selectbox("Copper ore grade", ["High (>2% Cu)", "Medium (1–2% Cu)", "Low (<1% Cu)"])

        production_route = st.selectbox("Production route", ["Virgin/Raw", "Recycled", "Mixed"])
        recycled_pct = st.slider("Recycled content (%)", 0, 100, 30)

    with col2:
        energy_source = st.selectbox("Energy source", ["Coal-based grid", "Mixed grid", "Renewable-heavy"])
        transport_km = st.number_input("Transport distance (km)", min_value=0, max_value=5000, value=200)
        transport_tonnes = st.number_input("Transport quantity (tonnes)", min_value=1, max_value=10000, value=1)

    with col3:
        eol_option = st.selectbox("End-of-life option", ["Landfill", "Recycling", "Reuse"])
        storage_practice = st.selectbox("Storage / residue handling",
                                        ["Proper authorized storage", "Temporary open storage", "Untreated disposal"])
        run_button = st.form_submit_button("Run LCA estimate")

# ---------------------------
# Calculation & results
# ---------------------------
if run_button:
    if metal == "Aluminium":
        if production_route == "Virgin/Raw":
            baseline = default_factors["aluminium_virgin_kgco2_per_kg"]
        elif production_route == "Recycled":
            baseline = default_factors["aluminium_recycled_kgco2_per_kg"]
        else:
            baseline = (default_factors["aluminium_virgin_kgco2_per_kg"] * (100 - recycled_pct) / 100 +
                        default_factors["aluminium_recycled_kgco2_per_kg"] * recycled_pct / 100)
    else:
        if production_route == "Virgin/Raw":
            baseline = default_factors["copper_virgin_kgco2_per_kg"]
        elif production_route == "Recycled":
            baseline = default_factors["copper_recycled_kgco2_per_kg"]
        else:
            baseline = (default_factors["copper_virgin_kgco2_per_kg"] * (100 - recycled_pct) / 100 +
                        default_factors["copper_recycled_kgco2_per_kg"] * recycled_pct / 100)

    red_mud_t, so2_kg_total = 0.0, 0.0
    if metal == "Aluminium":
        quality_factor = 1.0 if "High" in ore_quality else (1.2 if "Medium" in ore_quality else 1.5)
        red_mud_t = default_factors["red_mud_t_per_t_aluminium"] * transport_tonnes * quality_factor
    else:
        so2_factor = 1.0 if "High" in ore_quality else (1.3 if "Medium" in ore_quality else 1.6)
        so2_kg_total = default_factors["so2_kg_per_t_copper"] * transport_tonnes * so2_factor

    energy_factor_multiplier = 1.2 if energy_source == "Coal-based grid" else (1.0 if energy_source == "Mixed grid" else 0.8)
    kgco2_per_kg = baseline * energy_factor_multiplier
    transport_kgco2_per_ton = default_factors["transport_kgco2_per_tkm"] * transport_km
    total_co2_per_tonne = kgco2_per_kg * 1000 + transport_kgco2_per_ton

    circularity = recycled_pct * 0.5
    circularity += 30 if eol_option == "Recycling" else (40 if eol_option == "Reuse" else 0)
    circularity = min(100, circularity)

    recycle_cost = (default_factors["recycle_cost_usd_per_t_aluminium"] if metal == "Aluminium"
                    else default_factors["recycle_cost_usd_per_t_copper"]) * transport_tonnes

    # Display results
    st.header("Estimated Results (Illustrative)")
    st.metric("CO₂ per kg", f"{kgco2_per_kg:.2f} kg CO₂e")
    st.metric("CO₂ per tonne incl. transport", f"{total_co2_per_tonne:.0f} kg CO₂e")
    st.metric("Circularity Score", f"{circularity:.1f}")
    st.metric("Recycling cost (USD)", f"{recycle_cost:,.2f}")

    st.subheader("Breakdown (per tonne basis)")
    breakdown_df = pd.DataFrame({
        "Stage": ["Production+smelting", "Transport", "Total"],
        "Value (kg CO2e/t)": [kgco2_per_kg * 1000, transport_kgco2_per_ton, total_co2_per_tonne]
    })
    st.table(breakdown_df)

    st.subheader("By-products / Toxic emissions")
    if metal == "Aluminium":
        st.write(f"Red mud: **{red_mud_t:.2f} tonnes** for {transport_tonnes} t aluminium.")
    else:
        st.write(f"SO₂: **{so2_kg_total:.1f} kg** for {transport_tonnes} t copper smelted.")

    st.subheader("Compliance flags")
    if storage_practice != "Proper authorized storage":
        st.warning("⚠️ Storage not compliant with Hazardous Waste Rules (2016).")
    if metal == "Aluminium" and red_mud_t > 0:
        st.info("ℹ️ Red mud must follow CPCB handling guidelines.")
    if metal == "Copper" and so2_kg_total > 0:
        st.info("ℹ️ SO₂ capture recommended — conversion to sulphuric acid possible.")
    if circularity < 40:
        st.warning("⚠️ Low circularity score — increase recycled input.")

    # PDF Export
    if st.button("Export PDF Summary"):
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        pdf.multi_cell(0, 6, f"LCA Summary\nMetal: {metal}\nRoute: {production_route}\nRecycled%: {recycled_pct}\n"
                              f"Energy: {energy_source}\nTransport: {transport_km} km x {transport_tonnes} t\n"
                              f"CO₂ per kg: {kgco2_per_kg:.2f}\nCO₂ per t: {total_co2_per_tonne:.0f}\n"
                              f"Circularity score: {circularity:.1f}\n")
        if metal == "Aluminium":
            pdf.multi_cell(0, 6, f"Red mud: {red_mud_t:.2f} tonnes.")
        else:
            pdf.multi_cell(0, 6, f"SO₂: {so2_kg_total:.1f} kg.")
        pdf.output("SustainaMine_LCA_Summary.pdf")
        st.success("PDF exported successfully!")

st.markdown("---")
st.header("References")
for k, v in SOURCES.items():
    st.write(f"- **{k}** : {v}")
