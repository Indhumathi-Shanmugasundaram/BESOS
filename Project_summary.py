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
st.title("Project Summary")

# Sidebar navigation
st.sidebar.title("Navigation")
if st.sidebar.button("Project Configuration"):
    st.session_state.project_id = None
    st.switch_page("Project_configuration.py")
st.sidebar.button("Site Load")
st.sidebar.button("Optimize")

# Create Project Button
if st.button("Create Project"):
    st.session_state.project_id = None
    st.switch_page("Project_configuration.py")

# Load and display project summary
rows = get_project_summary()

if rows:
    df = build_dataframe(rows)
    for i, row in df.iterrows():
        with st.container():
            col1, col2 = st.columns([10, 2])
            with col1:
                st.markdown(
                    f"**{row['Project Name']}**  \n"
                    f"Type: {row['Project Type']}  \n"
                    f"State: {row['State']} | District: {row['District']}"
                )
            with col2:
                if st.button("Configure", key=f"config_{row['Project Id']}"):
                    st.session_state.project_id = row['Project Id']
                    st.switch_page("Project_configuration.py")
else:
    st.warning("No projects found.")
