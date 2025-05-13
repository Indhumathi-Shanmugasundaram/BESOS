# project configuration
import streamlit as st
import mysql.connector
from datetime import datetime

# MySQL connection
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

# Fetch state name → code mapping
def fetch_state_name_code_map():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT name, code FROM states")
    result = cursor.fetchall()
    conn.close()
    return {name: code for name, code in result}

# Fetch districts by state code
def get_districts_for_state(state_code):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM districts WHERE state_code = %s", (state_code,))
    districts = [row[0] for row in cursor.fetchall()]
    conn.close()
    return districts

# Check if project_id already exists
def project_exists(project_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT 1 FROM project_config WHERE project_id = %s", (project_id,))
    result = cursor.fetchone()
    conn.close()
    return result is not None

# Save new project
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

# Update existing project
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
st.sidebar.title("Navigation")
st.sidebar.button("Project Configuration")
st.sidebar.button("Site Load")
st.sidebar.button("Optimize")

# Title
st.title("Project Configuration Form")

# Dropdown data
project_types = fetch_options("SELECT type FROM project_types")
years = [str(y) for y in range(2022, 2032)]
states = fetch_options("SELECT name FROM states")
state_code_map = fetch_state_name_code_map()

# Session state initialization
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

# Form
with st.form("project_form"):
    project_id = st.text_input("Project ID *", value="ISN-ETS: SECI-2023-TN000020")
    project_name = st.text_input("Project Name *", value="Supply of 800 MW FDP ISTSconnected (RE) Power Projects")
    project_type = st.selectbox("Project Type *", project_types)
    construction_year = st.selectbox("Construction Year *", years)
    operation_year = st.selectbox("Operation Year *", years)

    project_description = st.text_area("Project Description", value="Supply of 800 MW Firm and Dispatchable Power from ISTSconnected Renewable Energy (RE) Power Projects in India.")

    st.markdown("### Energy Sources")
    wind = st.checkbox("Wind", value=True)
    solar = st.checkbox("Solar", value=True)
    battery = st.checkbox("Battery", value=True)

    st.markdown("### Site Information")
    site_name = st.text_input("Site Name", value="Kathura")
    site_address = st.text_area("Site Address")
    country = st.text_input("Country", value="India")

    st.session_state.selected_state = st.selectbox("Select State", states, key="state_select")

    if st.form_submit_button("Load Districts"):
        code = state_code_map.get(st.session_state.selected_state)
        st.session_state.districts = get_districts_for_state(code) if code else []
        st.session_state.selected_district = st.session_state.districts[0] if st.session_state.districts else ""

    selected_district = st.selectbox("Select District", st.session_state.districts, key="district_select")

    if st.form_submit_button("Save"):
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
                    datetime.now(),  # modified
                    project_id
                )
            }
        else:
            insert_data = (
                project_id, project_name, project_type, project_description,
                construction_year, operation_year, int(wind), int(solar), int(battery),
                site_name, site_address, country, st.session_state.selected_state, selected_district,
                datetime.now()  # created
            )
            insert_project(insert_data)
            st.success("Project configuration saved successfully!")

# Prompt to Modify
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


