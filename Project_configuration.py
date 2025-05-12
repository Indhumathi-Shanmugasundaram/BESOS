# project_summary.py
import streamlit as st
import pandas as pd
import mysql.connector

# --- MySQL connection ---
def get_connection():
    return mysql.connector.connect(
        host='localhost',
        user='root',
        password='Dharanesh@18',
        database='imdb'
    )

# --- Fetch project summary data ---
def get_project_summary():
    query = """
        SELECT 
            project_id, project_name, project_type, 
            construction_year, operation_year, 
            state, district, site_name, 'Open' AS status
        FROM project_config
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(query)
    results = cursor.fetchall()
    conn.close()
    return results

# --- Convert results to DataFrame ---
def build_dataframe(rows):
    columns = ["Project Id", "Project Name", "Project Type", 
               "Construction Year", "Operation Year", 
               "State", "District", "Site", "Status"]
    return pd.DataFrame(rows, columns=columns)

# --- Main UI ---
st.set_page_config(page_title="Project Summary", layout="wide")

# Header and title
st.markdown("""
    <h3 style='margin-bottom: 0;'>Hybrid Renewable Energy System - Capacity Optimization DSS</h3>
    <h4 style='color: gray; margin-top: 0;'>Project Summary</h4>
""", unsafe_allow_html=True)

# Sidebar navigation
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/6/6a/Retina_icon.png", width=100)
    st.markdown("### Navigation")
    if st.button("Project Configuration"):
        st.session_state.page = "project_config"
        st.switch_page("Project_configuration.py")
    if st.button("Site Load"):
        st.session_state.page = "project_load"
        st.switch_page("Project_load.py")
    if st.button("Optimize"):
        st.session_state.page = "optimize"
        st.switch_page("Optimize.py")

# Search bar
with st.container():
    st.markdown("### Search Criteria")
    col1, col2, col3 = st.columns([2, 4, 2])
    with col1:
        project_type = st.selectbox("Project Type", options=["--Select--", "Firm & Dispatchable Renewable Energy"])
    with col2:
        project_name = st.text_input("Project Name")
    with col3:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("Search"):
            pass  # Add filtering logic if needed

# Create Project Button
st.markdown("<div style='text-align: right;'>", unsafe_allow_html=True)
if st.button("Create Project"):
    st.session_state.project_id = None
    st.session_state.page = "project_config"
    st.switch_page("Project_configuration.py")
st.markdown("</div>", unsafe_allow_html=True)

# Load and display project summary
df = build_dataframe(get_project_summary())

# Display styled table with clickable project IDs
if not df.empty:
    st.markdown("""
        <style>
        .dataframe thead th {text-align: left;}
        </style>
    """, unsafe_allow_html=True)

    for i, row in df.iterrows():
        col1, col2, col3, col4, col5, col6, col7, col8, col9 = st.columns([2, 3, 3, 2, 2, 2, 2, 2, 2])
        with col1:
            if st.button(row["Project Id"], key=f"projid_{i}"):
                st.session_state.project_id = row["Project Id"]
                st.session_state.page = "project_config"
                st.switch_page("Project_configuration.py")
        with col2:
            st.write(row["Project Name"])
        with col3:
            st.write(row["Project Type"])
        with col4:
            st.write(row["Construction Year"])
        with col5:
            st.write(row["Operation Year"])
        with col6:
            st.write(row["State"])
        with col7:
            st.write(row["District"])
        with col8:
            st.write(row["Site"])
        with col9:
            st.write(row["Status"])

    st.caption("Showing 1 to {} of {} entries".format(len(df), len(df)))
else:
    st.warning("No projects found.")
