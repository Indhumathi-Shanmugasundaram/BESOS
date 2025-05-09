import streamlit as st
import mysql.connector
import pandas as pd
import io

# DB connection
def get_connection():
    return mysql.connector.connect(
        host='localhost',
        user='root',
        password='Dharanesh@18',
        database='imdb'
    )

# Fetch available project IDs
def get_project_ids():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT project_id FROM project_config")
    ids = [row[0] for row in cursor.fetchall()]
    conn.close()
    return ids

# Fetch description based on project_id
def get_project_description(project_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT project_description FROM project_config WHERE project_id = %s", (project_id,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else ""

# Save functions for database storage
def save_wind_entries(project_id, entries):
    errors = []
    success_count = 0
    field_errors = {}  # Dictionary to track field-level errors
    
    if not project_id:
        return ["No project ID selected"], 0, {}
    
    conn = get_connection()
    cursor = conn.cursor()
    
    for idx, entry in enumerate(entries):
        # Skip empty entries
        if not entry["manufacturer"] and not entry["model"] and not entry["capacity"] and not entry["filename"]:
            continue
        
        field_errors[idx] = {}
        # Validate entries
        if not entry["manufacturer"]:
            field_errors[idx]["manufacturer"] = "Manufacturer is required"
        if not entry["model"]:
            field_errors[idx]["model"] = "Model is required"
        if not entry["capacity"]:
            field_errors[idx]["capacity"] = "Capacity is required"
        else:
            try:
                capacity = float(entry["capacity"])
            except ValueError:
                field_errors[idx]["capacity"] = "Capacity must be a number"
        if not entry["filename"]:
            field_errors[idx]["filename"] = "File is required"
        
        # If no field errors for this entry, save to database
        if not field_errors[idx]:
            try:
                cursor.execute("""
                    INSERT INTO wind_profile (project_id, manufacturer, model, capacity_mwh, file_name)
                    VALUES (%s, %s, %s, %s, %s)
                """, (
                    project_id,
                    entry["manufacturer"],
                    entry["model"],
                    float(entry["capacity"]),
                    entry["filename"]
                ))
                success_count += 1
            except Exception as e:
                errors.append(f"Wind Entry {idx+1}: Database error - {str(e)}")
    
    if success_count > 0:
        conn.commit()
    cursor.close()
    conn.close()
    
    return errors, success_count, field_errors

def save_solar_entries(project_id, entries):
    errors = []
    success_count = 0
    field_errors = {}  # Dictionary to track field-level errors
    
    if not project_id:
        return ["No project ID selected"], 0, {}
    
    conn = get_connection()
    cursor = conn.cursor()
    
    for idx, entry in enumerate(entries):
        # Skip empty entries
        if not entry["manufacturer"] and not entry["model"] and not entry["capacity"] and not entry["filename"]:
            continue
        
        field_errors[idx] = {}
        # Validate entries
        if not entry["manufacturer"]:
            field_errors[idx]["manufacturer"] = "Manufacturer is required"
        if not entry["model"]:
            field_errors[idx]["model"] = "Model is required"
        if not entry["capacity"]:
            field_errors[idx]["capacity"] = "Capacity is required"
        else:
            try:
                capacity = float(entry["capacity"])
            except ValueError:
                field_errors[idx]["capacity"] = "Capacity must be a number"
        if not entry["filename"]:
            field_errors[idx]["filename"] = "File is required"
        
        # If no field errors for this entry, save to database
        if not field_errors[idx]:
            try:
                cursor.execute("""
                    INSERT INTO solar_profile (project_id, manufacturer, model, capacity_mwh, file_name)
                    VALUES (%s, %s, %s, %s, %s)
                """, (
                    project_id,
                    entry["manufacturer"],
                    entry["model"],
                    float(entry["capacity"]),
                    entry["filename"]
                ))
                success_count += 1
            except Exception as e:
                errors.append(f"Solar Entry {idx+1}: Database error - {str(e)}")
    
    if success_count > 0:
        conn.commit()
    cursor.close()
    conn.close()
    
    return errors, success_count, field_errors

def save_demand_entries(project_id, entries):
    errors = []
    success_count = 0
    field_errors = {}  # Dictionary to track field-level errors
    
    if not project_id:
        return ["No project ID selected"], 0, {}
    
    conn = get_connection()
    cursor = conn.cursor()
    
    for idx, entry in enumerate(entries):
        field_errors[idx] = {}
        # Validate entries
        if not entry["filename"]:
            field_errors[idx]["filename"] = "File is required"
            continue
        
        # If no field errors for this entry, save to database
        if not field_errors[idx]:
            try:
                cursor.execute("""
                    INSERT INTO demand_profile (project_id, file_name)
                    VALUES (%s, %s)
                """, (
                    project_id,
                    entry["filename"]
                ))
                success_count += 1
            except Exception as e:
                errors.append(f"Demand Entry {idx+1}: Database error - {str(e)}")
    
    if success_count > 0:
        conn.commit()
    cursor.close()
    conn.close()
    
    return errors, success_count, field_errors

# Initialize session states
if "wind_errors" not in st.session_state:
    st.session_state["wind_errors"] = {}
if "solar_errors" not in st.session_state:
    st.session_state["solar_errors"] = {}
if "demand_errors" not in st.session_state:
    st.session_state["demand_errors"] = {}

for key in ["wind_model_sets", "solar_model_sets", "demand_model_sets"]:
    if key not in st.session_state:
        if key == "demand_model_sets":
            st.session_state[key] = [{
                "filename": "",
                "file": None
            }]
        else:
            st.session_state[key] = [{
                "manufacturer": "",
                "model": "",
                "capacity": "",
                "filename": "",
                "file": None
            }]

def add_model_set(key):
    st.session_state[key].append({
        "manufacturer": "",
        "model": "",
        "capacity": "",
        "filename": "",
        "file": None
    })

def delete_model_set(index, key):
    if len(st.session_state[key]) > 1:
        st.session_state[key].pop(index)
        # Also remove any errors for this index
        if key == "wind_model_sets" and index in st.session_state["wind_errors"]:
            del st.session_state["wind_errors"][index]
        elif key == "solar_model_sets" and index in st.session_state["solar_errors"]:
            del st.session_state["solar_errors"][index]

def add_demand_set():
    st.session_state["demand_model_sets"].append({
        "filename": "",
        "file": None
    })

def delete_demand_set(index):
    if len(st.session_state["demand_model_sets"]) > 1:
        st.session_state["demand_model_sets"].pop(index)
        if index in st.session_state["demand_errors"]:
            del st.session_state["demand_errors"][index]

# UI
st.title("Site Load Details")

# Project Selection
project_ids = get_project_ids()
selected_project_id = st.selectbox("Project ID", project_ids)
description = get_project_description(selected_project_id)
st.text_input("Project Description", value=description, disabled=True)

# Tabs
tabs = st.tabs(["Wind Load Profile", "Solar Load Profile", "Demand"])

# === WIND TAB ===
with tabs[0]:
    st.markdown("### Wind Model Details")
    
    for idx, entry in enumerate(st.session_state["wind_model_sets"]):
        st.markdown(f"#### Entry {idx + 1}")
        col1, col2, col3 = st.columns(3)
        with col1:
            manufacturer = st.text_input(f"Manufacturer (Wind) {idx+1}", value=entry["manufacturer"], key=f"wind_manufacturer_{idx}")
            if idx in st.session_state["wind_errors"] and "manufacturer" in st.session_state["wind_errors"][idx]:
                st.error(st.session_state["wind_errors"][idx]["manufacturer"])
        with col2:
            model = st.text_input(f"Model (Wind) {idx+1}", value=entry["model"], key=f"wind_model_{idx}")
            if idx in st.session_state["wind_errors"] and "model" in st.session_state["wind_errors"][idx]:
                st.error(st.session_state["wind_errors"][idx]["model"])
        with col3:
            capacity = st.text_input(f"Capacity in MWh (Wind) {idx+1}", value=entry["capacity"], key=f"wind_capacity_{idx}")
            if idx in st.session_state["wind_errors"] and "capacity" in st.session_state["wind_errors"][idx]:
                st.error(st.session_state["wind_errors"][idx]["capacity"])

        st.session_state["wind_model_sets"][idx]["manufacturer"] = manufacturer
        st.session_state["wind_model_sets"][idx]["model"] = model
        st.session_state["wind_model_sets"][idx]["capacity"] = capacity

        file_col1, file_col2, file_col3 = st.columns([3, 2, 2])
        with file_col1:
            uploaded = st.file_uploader("Upload CSV (Wind)", type=["csv"], key=f"wind_file_{idx}")
            if uploaded:
                try:
                    content = uploaded.read()
                    st.session_state["wind_model_sets"][idx]["filename"] = uploaded.name
                    st.session_state["wind_model_sets"][idx]["file"] = io.BytesIO(content)
                except Exception as e:
                    st.error(f"Invalid file: {e}")
                    st.session_state["wind_model_sets"][idx]["filename"] = ""
                    st.session_state["wind_model_sets"][idx]["file"] = None
            if idx in st.session_state["wind_errors"] and "filename" in st.session_state["wind_errors"][idx]:
                st.error(st.session_state["wind_errors"][idx]["filename"])

        with file_col2:
            st.text_input("File Name", value=entry["filename"], key=f"wind_filename_{idx}", disabled=True)

        with file_col3:
            if entry["file"]:
                if st.button("View", key=f"wind_view_{idx}"):
                    try:
                        entry["file"].seek(0)
                        df = pd.read_csv(entry["file"])
                        st.dataframe(df.head(10))
                    except Exception as e:
                        st.error(f"Error reading file: {e}")
                st.download_button(
                    label="Download",
                    data=entry["file"],
                    file_name=entry["filename"],
                    mime="text/csv",
                    key=f"wind_download_{idx}"
                )

        if idx > 0 and st.button("Delete", key=f"wind_delete_{idx}"):
            delete_model_set(idx, "wind_model_sets")
            st.rerun()
        st.markdown("---")

    st.button("➕ Add More", on_click=lambda: add_model_set("wind_model_sets"), key="add_wind_model_set")
    
    # Wind Save Button
    if st.button("Save Wind Entries", key="save_wind_button"):
        if not selected_project_id:
            st.error("Please select a Project ID")
        else:
            errors, success_count, field_errors = save_wind_entries(selected_project_id, st.session_state["wind_model_sets"])
            st.session_state["wind_errors"] = field_errors
            
            if errors:
                for err in errors:
                    st.error(err)
            
            if success_count > 0:
                st.success(f"Successfully saved {success_count} wind entries to the database!")
                
                # Option to clear only wind entries after successful save
                if st.button("Clear wind entries and start new", key="clear_wind"):
                    st.session_state["wind_model_sets"] = [{
                        "manufacturer": "",
                        "model": "",
                        "capacity": "",
                        "filename": "",
                        "file": None
                    }]
                    st.session_state["wind_errors"] = {}
                    st.rerun()

# === SOLAR TAB ===
with tabs[1]:
    st.markdown("### Solar Model Details")
    for idx, entry in enumerate(st.session_state["solar_model_sets"]):
        st.markdown(f"#### Entry {idx + 1}")
        col1, col2, col3 = st.columns(3)
        with col1:
            manufacturer = st.text_input(f"Manufacturer (Solar) {idx+1}", value=entry["manufacturer"], key=f"solar_manufacturer_{idx}")
            if idx in st.session_state["solar_errors"] and "manufacturer" in st.session_state["solar_errors"][idx]:
                st.error(st.session_state["solar_errors"][idx]["manufacturer"])
        with col2:
            model = st.text_input(f"Model (Solar) {idx+1}", value=entry["model"], key=f"solar_model_{idx}")
            if idx in st.session_state["solar_errors"] and "model" in st.session_state["solar_errors"][idx]:
                st.error(st.session_state["solar_errors"][idx]["model"])
        with col3:
            capacity = st.text_input(f"Capacity in MWh (Solar) {idx+1}", value=entry["capacity"], key=f"solar_capacity_{idx}")
            if idx in st.session_state["solar_errors"] and "capacity" in st.session_state["solar_errors"][idx]:
                st.error(st.session_state["solar_errors"][idx]["capacity"])

        st.session_state["solar_model_sets"][idx]["manufacturer"] = manufacturer
        st.session_state["solar_model_sets"][idx]["model"] = model
        st.session_state["solar_model_sets"][idx]["capacity"] = capacity

        file_col1, file_col2, file_col3 = st.columns([3, 2, 2])
        with file_col1:
            uploaded = st.file_uploader("Upload CSV (Solar)", type=["csv"], key=f"solar_file_{idx}")
            if uploaded:
                try:
                    content = uploaded.read()
                    st.session_state["solar_model_sets"][idx]["filename"] = uploaded.name
                    st.session_state["solar_model_sets"][idx]["file"] = io.BytesIO(content)
                except Exception as e:
                    st.error(f"Invalid file: {e}")
                    st.session_state["solar_model_sets"][idx]["filename"] = ""
                    st.session_state["solar_model_sets"][idx]["file"] = None
            if idx in st.session_state["solar_errors"] and "filename" in st.session_state["solar_errors"][idx]:
                st.error(st.session_state["solar_errors"][idx]["filename"])

        with file_col2:
            st.text_input("File Name", value=entry["filename"], key=f"solar_filename_{idx}", disabled=True)

        with file_col3:
            if entry["file"]:
                if st.button("View", key=f"solar_view_{idx}"):
                    try:
                        entry["file"].seek(0)
                        df = pd.read_csv(entry["file"])
                        st.dataframe(df.head(10))
                    except Exception as e:
                        st.error(f"Error reading file: {e}")
                st.download_button(
                    label="Download",
                    data=entry["file"],
                    file_name=entry["filename"],
                    mime="text/csv",
                    key=f"solar_download_{idx}"
                )

        if idx > 0 and st.button("Delete", key=f"solar_delete_{idx}"):
            delete_model_set(idx, "solar_model_sets")
            st.rerun()
        st.markdown("---")

    st.button("➕ Add More", on_click=lambda: add_model_set("solar_model_sets"), key="add_solar_model_set")
    
    # Solar Save Button
    if st.button("Save Solar Entries", key="save_solar_button"):
        if not selected_project_id:
            st.error("Please select a Project ID")
        else:
            errors, success_count, field_errors = save_solar_entries(selected_project_id, st.session_state["solar_model_sets"])
            st.session_state["solar_errors"] = field_errors
            
            if errors:
                for err in errors:
                    st.error(err)
            
            if success_count > 0:
                st.success(f"Successfully saved {success_count} solar entries to the database!")
                
                # Option to clear only solar entries after successful save
                if st.button("Clear solar entries and start new", key="clear_solar"):
                    st.session_state["solar_model_sets"] = [{
                        "manufacturer": "",
                        "model": "",
                        "capacity": "",
                        "filename": "",
                        "file": None
                    }]
                    st.session_state["solar_errors"] = {}
                    st.rerun()

# === DEMAND TAB ===
with tabs[2]:
    st.markdown("### Demand Details")
    for idx, entry in enumerate(st.session_state["demand_model_sets"]):
        st.markdown(f"#### Entry {idx + 1}")
        file_col1, file_col2, file_col3 = st.columns([3, 2, 2])
        with file_col1:
            uploaded = st.file_uploader("Upload Demand CSV", type=["csv"], key=f"demand_file_{idx}")
            if uploaded:
                try:
                    content = uploaded.read()
                    st.session_state["demand_model_sets"][idx]["filename"] = uploaded.name
                    st.session_state["demand_model_sets"][idx]["file"] = io.BytesIO(content)
                except Exception as e:
                    st.error(f"Invalid file: {e}")
                    st.session_state["demand_model_sets"][idx]["filename"] = ""
                    st.session_state["demand_model_sets"][idx]["file"] = None
            if idx in st.session_state["demand_errors"] and "filename" in st.session_state["demand_errors"][idx]:
                st.error(st.session_state["demand_errors"][idx]["filename"])

        with file_col2:
            st.text_input("File Name", value=entry["filename"], key=f"demand_filename_{idx}", disabled=True)

        with file_col3:
            if entry["file"]:
                if st.button("View", key=f"demand_view_{idx}"):
                    try:
                        entry["file"].seek(0)
                        df = pd.read_csv(entry["file"])
                        st.dataframe(df.head(10))
                    except Exception as e:
                        st.error(f"Error reading file: {e}")
                st.download_button(
                    label="Download",
                    data=entry["file"],
                    file_name=entry["filename"],
                    mime="text/csv",
                    key=f"demand_download_{idx}"
                )

        if idx > 0 and st.button("Delete", key=f"demand_delete_{idx}"):
            delete_demand_set(idx)
            st.rerun()
        st.markdown("---")

    st.button("➕ Add More", on_click=add_demand_set, key="add_demand_model_set")
    
    # Demand Save Button
    if st.button("Save Demand Entries", key="save_demand_button"):
        if not selected_project_id:
            st.error("Please select a Project ID")
        else:
            errors, success_count, field_errors = save_demand_entries(selected_project_id, st.session_state["demand_model_sets"])
            st.session_state["demand_errors"] = field_errors
            
            if errors:
                for err in errors:
                    st.error(err)
            
            if success_count > 0:
                st.success(f"Successfully saved {success_count} demand entries to the database!")
                
                # Option to clear only demand entries after successful save
                if st.button("Clear demand entries and start new", key="clear_demand"):
                    st.session_state["demand_model_sets"] = [{
                        "filename": "",
                        "file": None
                    }]
                    st.session_state["demand_errors"] = {}
                    st.rerun()