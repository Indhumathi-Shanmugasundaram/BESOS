import streamlit as st
import mysql.connector
from datetime import datetime
import os
import sys


def nav_to(page):
    st.session_state.page = page

# Initialize page in session state if not present
if "page" not in st.session_state:
    st.session_state.page = "project_config"

# Check which page to display and import the appropriate module
if st.session_state.page == "project_load":
    import Project_load
    st.stop()

def get_connection():
    return mysql.connector.connect(
        host='localhost',
        user='root',
        password='Dharanesh@18',
        database='imdb'
    )

# Fetch dropdown values
def fetch_options(query):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(query)
    options = [row[0] for row in cursor.fetchall()]
    conn.close()
    return options

def fetch_state_name_code_map():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT name, code FROM states")
    result = cursor.fetchall()
    conn.close()
    return {name: code for name, code in result}

def get_districts_for_state(state_code):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM districts WHERE state_code = %s", (state_code,))
    districts = [row[0] for row in cursor.fetchall()]
    conn.close()
    return districts

def project_exists(project_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT 1 FROM project_config WHERE project_id = %s", (project_id,))
    result = cursor.fetchone()
    conn.close()
    return result is not None

def insert_project(data):
    conn = get_connection()
    cursor = conn.cursor()
    query = """
        INSERT INTO project_config (
            project_id, project_name, project_type, project_description,
            construction_year, operation_year, wind, solar, battery,
            site_name, site_address, country, state, district, created
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    cursor.execute(query, data)
    conn.commit()
    conn.close()

def update_project(data):
    conn = get_connection()
    cursor = conn.cursor()
    query = """
        UPDATE project_config SET
            project_name = %s,
            project_type = %s,
            project_description = %s,
            construction_year = %s,
            operation_year = %s,
            wind = %s,
            solar = %s,
            battery = %s,
            site_name = %s,
            site_address = %s,
            country = %s,
            state = %s,
            district = %s,
            modified = %s
        WHERE project_id = %s
    """
    cursor.execute(query, data)
    conn.commit()
    conn.close()

# Sidebar
with st.sidebar:
    st.markdown("### Navigation")
    if st.button("Project Configuration"):
        st.session_state.page = "project_summary"
        st.switch_page("Project_summary.py")
    if st.button("Site Load"):
        st.session_state.page = "project_load"
        st.switch_page("Project_load.py")
    if st.button("Optimize"):
        st.session_state.page = "project_optimize"
        st.switch_page("Project_optimize.py")

st.header("Project Configuration")

# Top-right "Load Details" button
col1, col2 = st.columns([7, 1])
with col2:
    if st.button("Load Details", use_container_width=True, type="primary"):
        nav_to("project_load")
        st.rerun()

# Fetch dropdown data
project_types = fetch_options("SELECT type FROM project_types")
years = [str(y) for y in range(2022, 2032)]
states = fetch_options("SELECT name FROM states")
state_code_map = fetch_state_name_code_map()

# Session state init
if "selected_state" not in st.session_state:
    st.session_state.selected_state = states[0]
if "districts" not in st.session_state:
    code = state_code_map.get(st.session_state.selected_state)
    st.session_state.districts = get_districts_for_state(code) if code else []
if "selected_district" not in st.session_state and st.session_state.districts:
    st.session_state.selected_district = st.session_state.districts[0]
if "show_modify_prompt" not in st.session_state:
    st.session_state.show_modify_prompt = False
if "pending_data" not in st.session_state:
    st.session_state.pending_data = None

# CSS styling
st.markdown("""
<style>
    .stApp {
        max-width: 100%;
    }
    .block-container {
        max-width: 100%;
        padding-top: 3rem;
        padding-bottom: 1rem;
    }
    .stForm {
        width: 100%;
        padding: 0;
        border-radius: 0;
    }
    .stTextArea textarea {
        min-height: 80px;
        max-height: 80px;
    }
    h1, h2 {
        font-size: 1.75rem;
        margin-bottom: 1rem;
        overflow-wrap: break-word;
    }
    div[data-testid="stForm"] {
        padding: 0 !important;
    }
    button[kind="secondaryFormSubmit"] {
        background-color: #f0f2f6;
        color: #31333F;
    }
    button[kind="primaryFormSubmit"] {
        background-color: #0068C9;
        color: white;
    }
    .stButton button {
        background-color: #0068C9;
        color: white;
        width: 100%;
    }
    div[data-testid="stSidebar"] {
        background-color: #0068C9;
        color: white;
    }
    div[data-testid="stSidebar"] button {
        background-color: transparent;
        color: white;
        border: none;
        text-align: left;
        padding: 10px;
    }
</style>
""", unsafe_allow_html=True)

# Project form
with st.form("project_form", border=False):
    st.markdown("### Project Details")
    col1, col2 = st.columns(2)
    with col1:
        project_id = st.text_input("Project ID *", value="ISN-ETS: SECI-2023-TN000020")
        project_name = st.text_input("Project Name *", value="Supply of 800 MW FDP ISTSconnected (RE) Power Projects")
        project_type = st.selectbox("Project Type *", project_types)
    with col2:
        construction_year = st.selectbox("Construction Year *", years)
        operation_year = st.selectbox("Operation Year *", years)
        project_description = st.text_area("Project Description", value="Supply of 800 MW Firm and Dispatchable Power from ISTSconnected Renewable Energy (RE) Power Projects in India.", height=80)

    st.markdown("### RE Component")
    re_cols = st.columns(3)
    with re_cols[0]: wind = st.checkbox("Wind", value=True)
    with re_cols[1]: solar = st.checkbox("Solar", value=True)
    with re_cols[2]: battery = st.checkbox("Battery", value=True)

    st.markdown("### Site Information")
    site_col1, site_col2, site_col3, site_col4 = st.columns(4)
    with site_col1: site_name = st.text_input("Site Name", value="Kathura")
    with site_col2: site_address = st.text_input("Site Address")
    with site_col3: country = st.selectbox("Country", ["India"], index=0)
    with site_col4: st.session_state.selected_state = st.selectbox("State", states, key="state_select")

    site_row2_col1, site_row2_col2, site_row2_col3, site_row2_col4 = st.columns(4)
    with site_row2_col1:
        selected_district = st.selectbox("District", st.session_state.districts, key="district_select")
    with site_row2_col2:
        st.write("")
        if st.form_submit_button("Load Districts", type="secondary"):
            code = state_code_map.get(st.session_state.selected_state)
            st.session_state.districts = get_districts_for_state(code) if code else []
            st.session_state.selected_district = st.session_state.districts[0] if st.session_state.districts else ""

    save_col1, save_col2, save_col3 = st.columns([6, 1, 1])
    with save_col2:
        save_button = st.form_submit_button("Save", use_container_width=True, type="primary")
    with save_col3:
        confirm_button = st.form_submit_button("Confirm", use_container_width=True)

    if save_button:
        if not project_id or not project_name or not project_type or not construction_year or not operation_year:
            st.error("Please fill in all mandatory fields: Project ID, Name, Type, Construction & Operation Year.")
        elif project_exists(project_id):
            st.warning("Project ID already exists. Do you want to modify the existing project?")
            st.session_state.show_modify_prompt = True
            st.session_state.pending_data = {
                "update_data": (
                    project_name, project_type, project_description,
                    construction_year, operation_year, int(wind), int(solar), int(battery),
                    site_name, site_address, country, st.session_state.selected_state, selected_district,
                    datetime.now(), project_id
                )
            }
        else:
            insert_data = (
                project_id, project_name, project_type, project_description,
                construction_year, operation_year, int(wind), int(solar), int(battery),
                site_name, site_address, country, st.session_state.selected_state, selected_district,
                datetime.now()
            )
            insert_project(insert_data)
            st.success("Project configuration saved successfully!")

if st.session_state.show_modify_prompt:
    st.markdown("#### A project with this ID already exists. What would you like to do?")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Modify"):
            update_project(st.session_state.pending_data["update_data"])
            st.success("Existing project modified successfully!")
            st.session_state.show_modify_prompt = False
            st.session_state.pending_data = None
    with col2:
        if st.button("Cancel"):
            st.info("No changes were saved.")
            st.session_state.show_modify_prompt = False
            st.session_state.pending_data = None
