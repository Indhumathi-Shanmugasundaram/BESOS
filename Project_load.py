import streamlit as st
import mysql.connector
import pandas as pd
import io

st.set_page_config(
    page_title="Site Load Details",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS to style buttons as blue
st.markdown("""
<style>
    div.stButton > button {
        background-color: #0066cc;
        color: white;
    }
    div.stButton > button:hover {
        background-color: #004c99;
        color: white;
    }
</style>
""", unsafe_allow_html=True)


# Initialize page in session state if not present
if "page" not in st.session_state:
    st.session_state.page = "project_load"

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

# Validation functions for wind, solar, battery, and demand entries
def validate_wind_entries(entries):
    errors = {}
    for idx, entry in enumerate(entries):
        entry_errors = {}
        
        # Skip entirely empty entries
        if not any([entry.get("manufacturer", ""), entry.get("model", ""), entry.get("capacity", ""), entry.get("filename", "")]):
            continue

        if not entry.get("manufacturer", "").strip():
            entry_errors["manufacturer"] = "Manufacturer is required"
        
        if not entry.get("model", "").strip():
            entry_errors["model"] = "Model is required"
        
        if not entry.get("capacity", "").strip():
            entry_errors["capacity"] = "Capacity is required"
        else:
            try:
                capacity = float(entry["capacity"])
                if capacity <= 0:
                    entry_errors["capacity"] = "Capacity must be a positive number"
            except ValueError:
                entry_errors["capacity"] = "Capacity must be a numeric value"


        if not entry.get("filename"):
            if st.session_state["wind_invalid_files"][idx]:
                entry_errors["filename"] = "Invalid file type. Only CSV or Excel files are allowed"
            else:
                entry_errors["filename"] = "Please upload a file"


        if entry_errors:
            errors[idx] = entry_errors
    return errors

def validate_solar_entries(entries):
    errors = {}
    for idx, entry in enumerate(entries):
        entry_errors = {}
        
        # Skip entirely empty entries
        if not any([entry.get("manufacturer", ""), entry.get("model", ""), entry.get("capacity", ""), entry.get("filename", "")]):
            continue

        if not entry.get("manufacturer", "").strip():
            entry_errors["manufacturer"] = "Manufacturer is required"
        
        if not entry.get("model", "").strip():
            entry_errors["model"] = "Model is required"
        
        if not entry.get("capacity", "").strip():
            entry_errors["capacity"] = "Capacity is required"
        else:
            try:
                capacity = float(entry["capacity"])
                if capacity <= 0:
                    entry_errors["capacity"] = "Capacity must be a positive number"
            except ValueError:
                entry_errors["capacity"] = "Capacity must be a numeric value"

        if not entry.get("filename"):
            entry_errors["filename"] = "File is required"
        elif not entry["filename"].lower().endswith(('.csv', '.xlsx')):
            entry_errors["filename"] = "Only CSV or Excel files are allowed"

        if entry_errors:
            errors[idx] = entry_errors
    return errors

def validate_battery_entries(entries):
    errors = {}
    for idx, entry in enumerate(entries):
        entry_errors = {}
        
        # Skip entirely empty entries
        if not any([entry.get("manufacturer", ""), entry.get("model", ""), entry.get("capacity", ""), entry.get("filename", "")]):
            continue

        if not entry.get("manufacturer", "").strip():
            entry_errors["manufacturer"] = "Manufacturer is required"
        
        if not entry.get("model", "").strip():
            entry_errors["model"] = "Model is required"
        
        if not entry.get("capacity", "").strip():
            entry_errors["capacity"] = "Capacity is required"
        else:
            try:
                capacity = float(entry["capacity"])
                if capacity <= 0:
                    entry_errors["capacity"] = "Capacity must be a positive number"
            except ValueError:
                entry_errors["capacity"] = "Capacity must be a numeric value"

        if not entry.get("filename"):
            entry_errors["filename"] = "File is required"
        elif not entry["filename"].lower().endswith(('.csv', '.xlsx')):
            entry_errors["filename"] = "Only CSV or Excel files are allowed"

        if entry_errors:
            errors[idx] = entry_errors
    return errors

def validate_demand_entries(entries):
    errors = {}
    for idx, entry in enumerate(entries):
        entry_errors = {}
        
        # Skip entirely empty entries
        if not any([entry.get("manufacturer", ""), entry.get("model", ""), entry.get("capacity", ""), entry.get("filename", "")]):
            continue

        if not entry.get("manufacturer", "").strip():
            entry_errors["manufacturer"] = "Manufacturer is required"
        
        if not entry.get("model", "").strip():
            entry_errors["model"] = "Model is required"
        
        if not entry.get("capacity", "").strip():
            entry_errors["capacity"] = "Capacity is required"
        else:
            try:
                capacity = float(entry["capacity"])
                if capacity <= 0:
                    entry_errors["capacity"] = "Capacity must be a positive number"
            except ValueError:
                entry_errors["capacity"] = "Capacity must be a numeric value"

        if not entry.get("filename"):
            entry_errors["filename"] = "File is required"
        elif not entry["filename"].lower().endswith(('.csv', '.xlsx')):
            entry_errors["filename"] = "Only CSV or Excel files are allowed"

        if entry_errors:
            errors[idx] = entry_errors
    return errors


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
                # Convert file content to binary for storage
                file_content = None
                if entry["file"]:
                    entry["file"].seek(0)
                    file_content = entry["file"].read()

                cursor.execute("""
                    INSERT INTO wind_profile (project_id, manufacturer, model, capacity_mwh, file_name, file_content)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (
                    project_id,
                    entry["manufacturer"],
                    entry["model"],
                    float(entry["capacity"]),
                    entry["filename"],
                    file_content
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
                # Convert file content to binary for storage
                file_content = None
                if entry["file"]:
                    entry["file"].seek(0)
                    file_content = entry["file"].read()

                cursor.execute("""
                    INSERT INTO solar_profile (project_id, manufacturer, model, capacity_mwh, file_name, file_content)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (
                    project_id,
                    entry["manufacturer"],
                    entry["model"],
                    float(entry["capacity"]),
                    entry["filename"],
                    file_content
                ))
                success_count += 1
            except Exception as e:
                errors.append(f"Solar Entry {idx+1}: Database error - {str(e)}")
    
    if success_count > 0:
        conn.commit()
    cursor.close()
    conn.close()
    
    return errors, success_count, field_errors

def save_battery_entries(project_id, entries):
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
                # Convert file content to binary for storage
                file_content = None
                if entry["file"]:
                    entry["file"].seek(0)
                    file_content = entry["file"].read()

                cursor.execute("""
                    INSERT INTO battery_profile (project_id, manufacturer, model, capacity_mwh, file_name, file_content)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (
                    project_id,
                    entry["manufacturer"],
                    entry["model"],
                    float(entry["capacity"]),
                    entry["filename"],
                    file_content
                ))
                success_count += 1
            except Exception as e:
                errors.append(f"Battery Entry {idx+1}: Database error - {str(e)}")
    
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
                # Convert file content to binary for storage
                file_content = None
                if entry["file"]:
                    entry["file"].seek(0)
                    file_content = entry["file"].read()

                cursor.execute("""
                    INSERT INTO demand_profile (project_id, file_name, file_content)
                    VALUES (%s, %s, %s)
                """, (
                    project_id,
                    entry["filename"],
                    file_content
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
if "page" not in st.session_state:
    st.session_state.page = "project_load"

# Initialize model sets with default values
for key in ["wind_model_sets", "solar_model_sets", "battery_model_sets", "demand_model_sets"]:
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

# Initialize error dictionaries
for key in ["wind_errors", "solar_errors", "battery_errors", "demand_errors"]:
    if key not in st.session_state:
        st.session_state[key] = {}

# Initialize invalid file flags
st.session_state["wind_invalid_files"] = [False] * len(st.session_state["wind_model_sets"])
st.session_state["solar_invalid_files"] = [False] * len(st.session_state["solar_model_sets"])
st.session_state["battery_invalid_files"] = [False] * len(st.session_state["battery_model_sets"])
st.session_state["demand_invalid_files"] = [False] * len(st.session_state["demand_model_sets"])

def add_model_set(key):
    st.session_state[key].append({
        "manufacturer": "",
        "model": "",
        "capacity": "",
        "filename": "",
        "file": None
    })
    # Add a corresponding invalid file flag
    if key == "wind_model_sets":
        st.session_state["wind_invalid_files"].append(False)
    elif key == "solar_model_sets":
        st.session_state["solar_invalid_files"].append(False)
    elif key == "battery_model_sets":
        st.session_state["battery_invalid_files"].append(False)


def delete_model_set(index, key):
    if len(st.session_state[key]) > 1:
        st.session_state[key].pop(index)
        # Also remove any errors for this index
        if key == "wind_model_sets" and index in st.session_state["wind_errors"]:
            del st.session_state["wind_errors"][index]
            # Remove the corresponding invalid file flag
            st.session_state["wind_invalid_files"].pop(index)
        elif key == "solar_model_sets" and index in st.session_state["solar_errors"]:
            del st.session_state["solar_errors"][index]
            # Remove the corresponding invalid file flag
            st.session_state["solar_invalid_files"].pop(index)
        elif key == "battery_model_sets" and index in st.session_state["battery_errors"]:
            del st.session_state["battery_errors"][index]
            # Remove the corresponding invalid file flag
            st.session_state["battery_invalid_files"].pop(index)

def add_demand_set():
    st.session_state["demand_model_sets"].append({
        "filename": "",
        "file": None
    })
    # Add a corresponding invalid file flag
    st.session_state["demand_invalid_files"].append(False)

def delete_demand_set(index):
    if len(st.session_state["demand_model_sets"]) > 1:
        st.session_state["demand_model_sets"].pop(index)
        if index in st.session_state["demand_errors"]:
            del st.session_state["demand_errors"][index]
        # Remove the corresponding invalid file flag
        st.session_state["demand_invalid_files"].pop(index)

st.title("Site Load Details")

# Sidebar navigation
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

# Add navigation button to go back to Project Configuration
if st.button("View Project Details"):
    st.switch_page("Project_configuration.py")


# Project Selection - horizontal layout
col1, col2 = st.columns(2)
with col1:
    project_ids = get_project_ids()
    selected_project_id = st.selectbox("Project ID", project_ids)
with col2:
    description = get_project_description(selected_project_id)
    st.text_input("Project Description", value=description, disabled=True)

tabs = st.tabs(["Wind Load Profile", "Solar Load Profile", "Battery", "Demand"])

# === WIND TAB ===
with tabs[0]:
    st.markdown("### Wind Model Details")
    
    for idx, entry in enumerate(st.session_state["wind_model_sets"]):
        if idx > 0:
            st.markdown("---")
            
        col1, col2, col3 = st.columns(3)
        with col1:
            manufacturer = st.text_input(f"Manufacturer {idx+1} (Wind)", value=entry["manufacturer"], key=f"wind_manufacturer_{idx}")
            if idx in st.session_state["wind_errors"] and "manufacturer" in st.session_state["wind_errors"][idx]:
                st.error(st.session_state["wind_errors"][idx]["manufacturer"])
        with col2:
            model = st.text_input(f"Model {idx+1} (Wind)", value=entry["model"], key=f"wind_model_{idx}")
            if idx in st.session_state["wind_errors"] and "model" in st.session_state["wind_errors"][idx]:
                st.error(st.session_state["wind_errors"][idx]["model"])
        with col3:
            capacity = st.text_input(f"Capacity {idx+1} in MWh (Wind)", value=entry["capacity"], key=f"wind_capacity_{idx}")
            if idx in st.session_state["wind_errors"] and "capacity" in st.session_state["wind_errors"][idx]:
                st.error(st.session_state["wind_errors"][idx]["capacity"])

        st.session_state["wind_model_sets"][idx]["manufacturer"] = manufacturer
        st.session_state["wind_model_sets"][idx]["model"] = model
        st.session_state["wind_model_sets"][idx]["capacity"] = capacity

        file_col1, file_col2, file_col3 = st.columns([3, 2, 2])
        with file_col1:

            uploaded = st.file_uploader(f"Upload CSV {idx+1} (Wind)", type=["csv", "xlsx"], key=f"wind_file_{idx}")
            if uploaded is None:
                st.session_state["wind_model_sets"][idx]["filename"] = ""
                st.session_state["wind_model_sets"][idx]["file"] = None
                st.session_state["wind_invalid_files"][idx] = False
            else:
                try:
                    valid_extensions = ['.csv', '.xlsx']
                    if not any(uploaded.name.lower().endswith(ext) for ext in valid_extensions):
                        st.error(f"Error: Only CSV or Excel files are allowed. You uploaded {uploaded.name}")
                        st.session_state["wind_invalid_files"][idx] = True
                        st.session_state["wind_model_sets"][idx]["filename"] = ""
                        st.session_state["wind_model_sets"][idx]["file"] = None
                    else:
                        content = uploaded.read()
                        st.session_state["wind_model_sets"][idx]["filename"] = uploaded.name
                        st.session_state["wind_model_sets"][idx]["file"] = io.BytesIO(content)
                        st.session_state["wind_invalid_files"][idx] = False
                except Exception as e:
                    st.error(f"Invalid file: {e}")
                    st.session_state["wind_invalid_files"][idx] = True
                    st.session_state["wind_model_sets"][idx]["filename"] = ""
                    st.session_state["wind_model_sets"][idx]["file"] = None
            if idx in st.session_state["wind_errors"] and "filename" in st.session_state["wind_errors"][idx]:
                st.error(st.session_state["wind_errors"][idx]["filename"])

        with file_col2:
            st.text_input(f"File Name {idx+1}", value=entry["filename"], key=f"wind_filename_{idx}", disabled=True)


        with file_col3:
            if entry["file"]:
                st.download_button(
                    label="Download",
                    data=entry["file"],
                    file_name=entry["filename"],
                    mime="text/csv",
                    key=f"wind_download_{idx}"
                )
        
        # Display preview of file automatically after upload
        if entry["file"]:
            try:
                entry["file"].seek(0)
                if entry["filename"].lower().endswith('.csv'):
                    df = pd.read_csv(entry["file"])
                else:  # Excel file
                    df = pd.read_excel(entry["file"])
                st.dataframe(df.head(10))
                entry["file"].seek(0)  # Reset file pointer after reading
            except Exception as e:
                st.error(f"Error previewing file: {e}")


        if idx > 0 and st.button("Delete", key=f"wind_delete_{idx}"):
            delete_model_set(idx, "wind_model_sets")
            st.rerun()


    # Add and Save buttons
    btn_col1, btn_col2 = st.columns(2)
    with btn_col1:
        st.button("➕ Add More", on_click=lambda: add_model_set("wind_model_sets"), key="add_wind_model_set")
    with btn_col2:
        if st.button("Save Wind Entries", key="save_wind_button"):
            if not selected_project_id:
                st.error("Please select a Project ID")
            elif True in st.session_state["wind_invalid_files"]:
                st.error("Cannot save! Invalid files have been detected. Please upload valid CSV files only.")
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
                        st.session_state["wind_invalid_files"] = [False]
                        st.rerun()

# === SOLAR TAB ===
with tabs[1]:
    st.markdown("### Solar Model Details")
    for idx, entry in enumerate(st.session_state["solar_model_sets"]):
        if idx > 0:
            st.markdown("---")
            
        col1, col2, col3 = st.columns(3)
        with col1:
            manufacturer = st.text_input(f"Manufacturer {idx+1} (Solar)", value=entry["manufacturer"], key=f"solar_manufacturer_{idx}")
            if idx in st.session_state["solar_errors"] and "manufacturer" in st.session_state["solar_errors"][idx]:
                st.error(st.session_state["solar_errors"][idx]["manufacturer"])
        with col2:
            model = st.text_input(f"Model {idx+1} (Solar)", value=entry["model"], key=f"solar_model_{idx}")
            if idx in st.session_state["solar_errors"] and "model" in st.session_state["solar_errors"][idx]:
                st.error(st.session_state["solar_errors"][idx]["model"])
        with col3:
            capacity = st.text_input(f"Capacity {idx+1} in MWh (Solar)", value=entry["capacity"], key=f"solar_capacity_{idx}")
            if idx in st.session_state["solar_errors"] and "capacity" in st.session_state["solar_errors"][idx]:
                st.error(st.session_state["solar_errors"][idx]["capacity"])

        st.session_state["solar_model_sets"][idx]["manufacturer"] = manufacturer
        st.session_state["solar_model_sets"][idx]["model"] = model
        st.session_state["solar_model_sets"][idx]["capacity"] = capacity

        file_col1, file_col2, file_col3 = st.columns([3, 2, 2])
        with file_col1:


            uploaded = st.file_uploader(f"Upload CSV {idx+1} (Solar)", type=["csv", "xlsx"], key=f"solar_file_{idx}")
            if uploaded is None:
                st.session_state["solar_model_sets"][idx]["filename"] = ""
                st.session_state["solar_model_sets"][idx]["file"] = None
                st.session_state["solar_invalid_files"][idx] = False
            else:
                try:
                    valid_extensions = ['.csv', '.xlsx']
                    if not any(uploaded.name.lower().endswith(ext) for ext in valid_extensions):
                        st.error(f"Error: Only CSV or Excel files are allowed. You uploaded {uploaded.name}")
                        st.session_state["solar_invalid_files"][idx] = True
                        st.session_state["solar_model_sets"][idx]["filename"] = ""
                        st.session_state["solar_model_sets"][idx]["file"] = None
                    else:
                        content = uploaded.read()
                        st.session_state["solar_model_sets"][idx]["filename"] = uploaded.name
                        st.session_state["solar_model_sets"][idx]["file"] = io.BytesIO(content)
                        st.session_state["solar_invalid_files"][idx] = False
                except Exception as e:
                    st.error(f"Invalid file: {e}")
                    st.session_state["solar_invalid_files"][idx] = True
                    st.session_state["solar_model_sets"][idx]["filename"] = ""
                    st.session_state["solar_model_sets"][idx]["file"] = None

            if idx in st.session_state["solar_errors"] and "filename" in st.session_state["solar_errors"][idx]:
                st.error(st.session_state["solar_errors"][idx]["filename"])

        with file_col2:
            st.text_input(f"File Name {idx+1}", value=entry["filename"], key=f"solar_filename_{idx}", disabled=True)


        with file_col3:
            if entry["file"]:
                st.download_button(
                    label="Download",
                    data=entry["file"],
                    file_name=entry["filename"],
                    mime="text/csv",
                    key=f"solar_download_{idx}"
                )

        # Display preview of file automatically after upload
        if entry["file"]:
            try:
                entry["file"].seek(0)
                if entry["filename"].lower().endswith('.csv'):
                    df = pd.read_csv(entry["file"])
                else:  # Excel file
                    df = pd.read_excel(entry["file"])
                st.dataframe(df.head(10))
                entry["file"].seek(0)  # Reset file pointer after reading
            except Exception as e:
                st.error(f"Error previewing file: {e}")

        if idx > 0 and st.button("Delete", key=f"solar_delete_{idx}"):
            delete_model_set(idx, "solar_model_sets")
            st.rerun()


# Add and Save buttons
    btn_col1, btn_col2 = st.columns(2)
    with btn_col1:
        st.button("➕ Add More", on_click=lambda: add_model_set("solar_model_sets"), key="add_solar_model_set")
    with btn_col2:
        if st.button("Save Solar Entries", key="save_solar_button"):
            if not selected_project_id:
                st.error("Please select a Project ID")
            elif True in st.session_state["solar_invalid_files"]:
                st.error("Cannot save! Invalid files have been detected. Please upload valid CSV files only.")
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
                        st.session_state["solar_invalid_files"] = [False]
                        st.rerun()

# === BATTERY TAB ===
with tabs[2]:
    st.markdown("### Battery Model Details")
    for idx, entry in enumerate(st.session_state["battery_model_sets"]):
        if idx > 0:
            st.markdown("---")
            
        col1, col2, col3 = st.columns(3)
        with col1:
            manufacturer = st.text_input(f"Manufacturer {idx+1} (Battery)", value=entry["manufacturer"], key=f"battery_manufacturer_{idx}")
            if idx in st.session_state["battery_errors"] and "manufacturer" in st.session_state["battery_errors"][idx]:
                st.error(st.session_state["battery_errors"][idx]["manufacturer"])
        with col2:
            model = st.text_input(f"Model {idx+1} (Battery)", value=entry["model"], key=f"battery_model_{idx}")
            if idx in st.session_state["battery_errors"] and "model" in st.session_state["battery_errors"][idx]:
                st.error(st.session_state["battery_errors"][idx]["model"])
        with col3:
            capacity = st.text_input(f"Capacity {idx+1} in MWh (Battery)", value=entry["capacity"], key=f"battery_capacity_{idx}")
            if idx in st.session_state["battery_errors"] and "capacity" in st.session_state["battery_errors"][idx]:
                st.error(st.session_state["battery_errors"][idx]["capacity"])

        st.session_state["battery_model_sets"][idx]["manufacturer"] = manufacturer
        st.session_state["battery_model_sets"][idx]["model"] = model
        st.session_state["battery_model_sets"][idx]["capacity"] = capacity

        file_col1, file_col2, file_col3 = st.columns([3, 2, 2])
        with file_col1:

            uploaded = st.file_uploader(f"Upload CSV {idx+1} (Battery)", type=["csv", "xlsx"], key=f"battery_file_{idx}")
            if uploaded is None:
                st.session_state["battery_model_sets"][idx]["filename"] = ""
                st.session_state["battery_model_sets"][idx]["file"] = None
                st.session_state["battery_invalid_files"][idx] = False
            else:
                try:
                    valid_extensions = ['.csv', '.xlsx']
                    if not any(uploaded.name.lower().endswith(ext) for ext in valid_extensions):
                        st.error(f"Error: Only CSV or Excel files are allowed. You uploaded {uploaded.name}")
                        st.session_state["battery_invalid_files"][idx] = True
                        st.session_state["battery_model_sets"][idx]["filename"] = ""
                        st.session_state["battery_model_sets"][idx]["file"] = None
                    else:
                        content = uploaded.read()
                        st.session_state["battery_model_sets"][idx]["filename"] = uploaded.name
                        st.session_state["battery_model_sets"][idx]["file"] = io.BytesIO(content)
                        st.session_state["battery_invalid_files"][idx] = False
                except Exception as e:
                    st.error(f"Invalid file: {e}")
                    st.session_state["battery_invalid_files"][idx] = True
                    st.session_state["battery_model_sets"][idx]["filename"] = ""
                    st.session_state["battery_model_sets"][idx]["file"] = None

            if idx in st.session_state["battery_errors"] and "filename" in st.session_state["battery_errors"][idx]:
                st.error(st.session_state["battery_errors"][idx]["filename"])

        with file_col2:
            st.text_input(f"File Name {idx+1}", value=entry["filename"], key=f"battery_filename_{idx}", disabled=True)


        with file_col3:
            if entry["file"]:
                st.download_button(
                    label="Download",
                    data=entry["file"],
                    file_name=entry["filename"],
                    mime="text/csv",
                    key=f"battery_download_{idx}"
                )
                
        # Display preview of file automatically after upload
        if entry["file"]:
            try:
                entry["file"].seek(0)
                if entry["filename"].lower().endswith('.csv'):
                    df = pd.read_csv(entry["file"])
                else:  # Excel file
                    df = pd.read_excel(entry["file"])
                st.dataframe(df.head(10))
                entry["file"].seek(0)  # Reset file pointer after reading
            except Exception as e:
                st.error(f"Error previewing file: {e}")

        if idx > 0 and st.button("Delete", key=f"battery_delete_{idx}"):
            delete_model_set(idx, "battery_model_sets")
            st.rerun()

 
    # Add and Save buttons
    btn_col1, btn_col2 = st.columns(2)
    with btn_col1:
        st.button("➕ Add More", on_click=lambda: add_model_set("battery_model_sets"), key="add_battery_model_set")
    with btn_col2:
        if st.button("Save Battery Entries", key="save_battery_button"):
            if not selected_project_id:
                st.error("Please select a Project ID")
            elif True in st.session_state["battery_invalid_files"]:
                st.error("Cannot save! Invalid files have been detected. Please upload valid CSV files only.")
            else:
                errors, success_count, field_errors = save_battery_entries(selected_project_id, st.session_state["battery_model_sets"])
                st.session_state["battery_errors"] = field_errors
                
                if errors:
                    for err in errors:
                        st.error(err)
                
                if success_count > 0:
                    st.success(f"Successfully saved {success_count} battery entries to the database!")
                    
                    # Option to clear only battery entries after successful save
                    if st.button("Clear battery entries and start new", key="clear_battery"):
                        st.session_state["battery_model_sets"] = [{
                            "manufacturer": "",
                            "model": "",
                            "capacity": "",
                            "filename": "",
                            "file": None
                        }]
                        st.session_state["battery_errors"] = {}
                        st.session_state["battery_invalid_files"] = [False]
                        st.rerun()

# === DEMAND TAB ===
with tabs[3]:
    st.markdown("### Demand Details")
    for idx, entry in enumerate(st.session_state["demand_model_sets"]):
        if idx > 0:
            st.markdown("---")
            
        file_col1, file_col2, file_col3 = st.columns([3, 2, 2])
        with file_col1:
 
            uploaded = st.file_uploader(f"Upload Demand CSV {idx+1}", type=["csv", "xlsx"], key=f"demand_file_{idx}")
            if uploaded is None:
                st.session_state["demand_model_sets"][idx]["filename"] = ""
                st.session_state["demand_model_sets"][idx]["file"] = None
                st.session_state["demand_invalid_files"][idx] = False
            else:
                try:
                    valid_extensions = ['.csv', '.xlsx']
                    if not any(uploaded.name.lower().endswith(ext) for ext in valid_extensions):
                        st.error(f"Error: Only CSV or Excel files are allowed. You uploaded {uploaded.name}")
                        st.session_state["demand_invalid_files"][idx] = True
                        st.session_state["demand_model_sets"][idx]["filename"] = ""
                        st.session_state["demand_model_sets"][idx]["file"] = None
                    else:
                        content = uploaded.read()
                        st.session_state["demand_model_sets"][idx]["filename"] = uploaded.name
                        st.session_state["demand_model_sets"][idx]["file"] = io.BytesIO(content)
                        st.session_state["demand_invalid_files"][idx] = False
                except Exception as e:
                    st.error(f"Invalid file: {e}")
                    st.session_state["demand_invalid_files"][idx] = True
                    st.session_state["demand_model_sets"][idx]["filename"] = ""
                    st.session_state["demand_model_sets"][idx]["file"] = None

            if idx in st.session_state["demand_errors"] and "filename" in st.session_state["demand_errors"][idx]:
                st.error(st.session_state["demand_errors"][idx]["filename"])

        with file_col2:
            st.text_input(f"File Name {idx+1}", value=entry["filename"], key=f"demand_filename_{idx}", disabled=True)

 
        with file_col3:
            if entry["file"]:
                st.download_button(
                    label="Download",
                    data=entry["file"],
                    file_name=entry["filename"],
                    mime="text/csv",
                    key=f"demand_download_{idx}"
                )

        # Display preview of file automatically after upload
        if entry["file"]:
            try:
                entry["file"].seek(0)
                if entry["filename"].lower().endswith('.csv'):
                    df = pd.read_csv(entry["file"])
                else:  # Excel file
                    df = pd.read_excel(entry["file"])
                st.dataframe(df.head(10))
                entry["file"].seek(0)  # Reset file pointer after reading
            except Exception as e:
                st.error(f"Error previewing file: {e}")

        if idx > 0 and st.button("Delete", key=f"demand_delete_{idx}"):
            delete_demand_set(idx)
            st.rerun()

 
# Add and Save buttons
    btn_col1, btn_col2 = st.columns(2)
    with btn_col1:
        st.button("➕ Add More", on_click=add_demand_set, key="add_demand_model_set")
    with btn_col2:
        if st.button("Save Demand Entries", key="save_demand_button"):
            if not selected_project_id:
                st.error("Please select a Project ID")
            elif True in st.session_state["demand_invalid_files"]:
                st.error("Cannot save! Invalid files have been detected. Please upload valid CSV files only.")
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
                        st.session_state["demand_invalid_files"] = [False]
                        st.rerun()