#project configuration
import streamlit as st
import mysql.connector


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

# Save project data
def save_to_database(data):
    conn = get_connection()
    cursor = conn.cursor()
    query = """
        INSERT INTO project_config (
            project_id, project_name, project_type, project_description,
            construction_year, operation_year, wind, solar, battery,
            site_name, site_address, country, state, district
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE
            project_name = VALUES(project_name),
            project_type = VALUES(project_type),
            project_description = VALUES(project_description),
            construction_year = VALUES(construction_year),
            operation_year = VALUES(operation_year),
            wind = VALUES(wind),
            solar = VALUES(solar),
            battery = VALUES(battery),
            site_name = VALUES(site_name),
            site_address = VALUES(site_address),
            country = VALUES(country),
            state = VALUES(state),
            district = VALUES(district)
    """
    cursor.execute(query, data)
    conn.commit()
    conn.commit()
    conn.close()

# Sidebar
st.sidebar.title("Navigation")
st.sidebar.button("Project Configuration")
st.sidebar.button("Site Load")
st.sidebar.button("Optimize")

# Title
st.title("Project Configuration Form")

# Fetch dropdown data
project_types = fetch_options("SELECT type FROM project_types")
years = [str(y) for y in range(2022, 2032)]
states = fetch_options("SELECT name FROM states")
state_code_map = fetch_state_name_code_map()

# Initialize session state variables
if "selected_state" not in st.session_state:
    st.session_state.selected_state = states[0]

if "districts" not in st.session_state:
    code = state_code_map.get(st.session_state.selected_state)
    st.session_state.districts = get_districts_for_state(code) if code else []

if "selected_district" not in st.session_state and st.session_state.districts:
    st.session_state.selected_district = st.session_state.districts[0]

# Form
with st.form("project_form"):
    # Add your new fields here
    project_id = st.text_input("Project ID *", value="ISN-ETS: SECI-2023-TN000020", placeholder="Enter Project ID")
    project_name = st.text_input("Project Name *", value="Supply of 800 MW FDP ISTSconnected (RE) Power Projects", placeholder="Enter Project Name")
    project_type = st.selectbox("Project Type *", project_types)
    construction_year = st.selectbox("Construction Year *", years)
    operation_year = st.selectbox("Operation Year *", years)

    project_description = st.text_area("Project Description", value="Supply of 800 MW Firm and Dispatchable Power from ISTSconnected Renewable Energy (RE) Power Projects in India, under Tariff-based Competitive Bidding (SECI-FDRE-III)")

    st.markdown("### Energy Sources")
    wind = st.checkbox("Wind", value=True)
    solar = st.checkbox("Solar", value=True)
    battery = st.checkbox("Battery", value=True)

    st.markdown("### Site Information")
    site_name = st.text_input("Site Name", value="Kathura")
    site_address = st.text_area("Site Address")
    country = st.text_input("Country", value="India")

    # Select State
    st.session_state.selected_state = st.selectbox("Select State", states, key="state_select")

    # Load Districts Button (inside form, after state)
    if st.form_submit_button("Load Districts"):
        code = state_code_map.get(st.session_state.selected_state)
        st.session_state.districts = get_districts_for_state(code) if code else []
        st.session_state.selected_district = st.session_state.districts[0] if st.session_state.districts else ""

    # Select District
    selected_district = st.selectbox("Select District", st.session_state.districts, key="district_select")

    # Save Form (only one submission button for the whole form)
    if st.form_submit_button("Save"):
        if not project_id or not project_name or not project_type or not construction_year or not operation_year:
            st.error("Please fill in all mandatory fields: Project ID, Name, Type, Construction & Operation Year.")
        else:
            data = (
                project_id, project_name, project_type, project_description,
                construction_year, operation_year, int(wind), int(solar), int(battery),
                site_name, site_address, country, st.session_state.selected_state, selected_district
            )
            save_to_database(data)
            st.success("Project configuration saved successfully!")

