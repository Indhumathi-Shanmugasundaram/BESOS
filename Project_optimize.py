import streamlit as st

# Page setup
st.set_page_config(page_title="Optimizer Summary", layout="wide")

# Sidebar Navigation
with st.sidebar:
    st.markdown("### Navigation")
    if st.button("Project Configuration"):
        st.switch_page("Project_configuration.py")
    if st.button("Site Load"):
        st.switch_page("Project_load.py")
    if st.button("Optimize"):
        st.switch_page("Project_optimize.py")

# Page Title
st.title("Optimizer Summary")

# Top Navigation Buttons
nav_col1, nav_col2 = st.columns(2)
with nav_col1:
    if st.button("View Project Details", key="view_project_btn"):
        st.switch_page("Project_configuration.py")
with nav_col2:
    if st.button("View Load Details", key="view_load_btn"):
        st.switch_page("Project_load.py")

# Project Details Section
st.subheader("Project Details")
col1, col2, col3 = st.columns(3)

with col1:
    project_id = st.text_input("Project Id *", "ISN-ETS: SECI-2023-TN000020", key="project_id")
with col2:
    project_name = st.text_input("Project Name *", "Supply of 800 MW FDP ISTSconnected ...", key="project_name")
with col3:
    run_number = st.selectbox("Run#", ["--Select--", "Run 1", "Run 2", "Run 3"], key="run_number")

col4, col5 = st.columns([3, 1])
with col4:
    date = st.date_input("Date", key="run_date")
with col5:
    st.markdown("###")
    st.button("View Results", key="view_results")

# Tabs for optimizer inputs
tabs = st.tabs(["RE Technical", "RE Project Economics", "RE Project Financials"])

# --- RE Technical Tab ---
with tabs[0]:
    st.markdown("### RE Technical - Wind")
    col1, col2, col3 = st.columns(3)
    with col1:
        wind_cuf = st.text_input("Capacity Utilization Factor(%)", "28.41", key="wind_cuf")
    with col2:
        wind_grid_avail = st.text_input("Grid Availability Factor(%)", "95", key="wind_grid")
    with col3:
        wind_deg = st.text_input("Annual Degradation(%)", "1", key="wind_deg")

    st.markdown("### RE Technical - Solar")
    col4, col5, col6 = st.columns(3)
    with col4:
        solar_cuf = st.text_input("Capacity Utilization Factor(%)", "20.42", key="solar_cuf")
    with col5:
        solar_grid_avail = st.text_input("Grid Availability Factor(%)", "95", key="solar_grid")
    with col6:
        solar_deg = st.text_input("Annual Degradation(%)", "1", key="solar_deg")

    st.markdown("### ES- Technical - Battery")
    col7, col8 = st.columns(2)
    with col7:
        battery_eff = st.text_input("Roundtrip Efficiency(%)", "97", key="battery_eff")
    with col8:
        battery_dod = st.text_input("Depth of Discharge(%)", "80", key="battery_dod")

    st.markdown("###")
    st.button("Run Optimizer", key="run_optimizer_technical")

# --- RE Project Economics Tab ---
with tabs[1]:
    st.markdown("### Economics")
    col1, col2, col3 = st.columns(3)
    with col1:
        cost_wind = st.text_input("Capital Cost - Wind (INR in Crore /MW)", "6.50", key="cost_wind")
        om_wind = st.text_input("O&M - Wind % of capital costs/ MW", "0.10", key="om_wind")
        insurance = st.text_input("Insurance(%)", "0.35", key="insurance")
    with col2:
        cost_solar = st.text_input("Capital Cost - Solar (INR in Crore /MW)", "3.50", key="cost_solar")
        om_solar = st.text_input("O&M - Solar % of capital costs/ MW", "0.04", key="om_solar")
    with col3:
        cost_battery = st.text_input("Capital Cost - Battery (INR in Crore /MW)", "0.60", key="cost_battery")
        om_battery = st.text_input("O&M - Battery % of capital costs/ MW", "0.01", key="om_battery")

    st.markdown("###")
    st.button("Run Optimizer", key="run_optimizer_economics")

# --- RE Project Financials Tab ---
with tabs[2]:
    st.markdown("### Financials")
    col1, col2, col3 = st.columns(3)
    with col1:
        equity = st.text_input("Equity(%)", "20", key="equity")
        depreciation = st.text_input("Depreciation (Year)", "30.00", key="depreciation")
        ppa_price = st.text_input("PPA Price (INR/MW)", "3000", key="ppa_price")
    with col2:
        loan_tenure = st.text_input("Loan Tenure(Year)", "15", key="loan_tenure")
        project_life = st.text_input("Project Life(Year)", "20", key="project_life")
        penalty = st.text_input("Penalty (INR/MW)", "4500", key="penalty")
    with col3:
        interest = st.text_input("Interest on Loan(%)", "4.5", key="interest_loan")
        inflation = st.text_input("Inflation Rate(%)", "5.5", key="inflation_rate")
        excess_price = st.text_input("Excess Generation Price(INR/MW)", "1500", key="excess_gen_price")

    st.markdown("###")
    st.button("Run Optimizer", key="run_optimizer_financials")
