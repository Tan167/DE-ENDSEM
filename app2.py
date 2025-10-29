import streamlit as st
from pymongo import MongoClient
from datetime import datetime
import pandas as pd

# --- MongoDB Setup ---
# ⚠️ REPLACE with your actual MongoDB connection string
MONGO_URI = "mongodb://localhost:27017"
DB_NAME = "AttendanceDB"
COLLECTION_NAME = "remote_logs"

@st.cache_resource
def get_mongo_client():
    """Initializes and caches the MongoDB client."""
    # Ensure you've replaced MONGO_URI above
    client = MongoClient(MONGO_URI)
    return client

# --- Database Functions ---

def log_attendance(worker_id, worker_name, department, status):
    """Inserts an attendance record (including department) into MongoDB."""
    try:
        client = get_mongo_client()
        db = client[DB_NAME]
        collection = db[COLLECTION_NAME]

        log_entry = {
            "worker_id": worker_id,
            "worker_name": worker_name,
            "department": department,  # <-- NEW FIELD
            "timestamp": datetime.now(),
            "status": status, # e.g., 'IN' or 'OUT'
            "date": datetime.now().date().isoformat()
        }
        result = collection.insert_one(log_entry)
        return result.acknowledged
    except Exception as e:
        st.error(f"Database error: {e}")
        return False

# --- Streamlit UI ---

def main():
    st.set_page_config(page_title="Remote Attendance System", layout="centered")
    st.title("👨‍💻 Remote Worker Attendance System")

    # Initialize session state for simple login
    if 'logged_in' not in st.session_state:
        st.session_state['logged_in'] = False
        st.session_state['worker_id'] = None
        st.session_state['worker_name'] = None
        st.session_state['department'] = None  # <-- NEW SESSION STATE

    if not st.session_state['logged_in']:
        st.header("Login")
        
        # Simple Mock Login Form
        worker_id_input = st.text_input("Worker ID (e.g., RMT-001)")
        worker_name_input = st.text_input("Full Name")
        
        # Department Selectbox
        departments = ["HR", "IT", "Sales", "Admin", "Management"]
        department_select = st.selectbox(
            "Select Department", 
            options=departments, 
            index=0 # Defaults to HR
        )
        
        if st.button("Log In", use_container_width=True):
            if worker_id_input and worker_name_input and department_select:
                st.session_state['logged_in'] = True
                st.session_state['worker_id'] = worker_id_input.upper().strip()
                st.session_state['worker_name'] = worker_name_input.strip()
                st.session_state['department'] = department_select # <-- STORE DEPARTMENT
                st.experimental_rerun() # Refresh the page to show the attendance view
            else:
                st.error("Please enter Worker ID, Full Name, and select a Department.")
    
    else:
        # --- Attendance Marker View ---
        worker_id = st.session_state['worker_id']
        worker_name = st.session_state['worker_name']
        department = st.session_state['department'] # <-- RETRIEVE DEPARTMENT

        st.success(f"Welcome, **{worker_name}** ({worker_id}) from **{department}**")
        st.subheader("Mark Your Attendance")
        st.markdown(f"Current Time: **{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}**")

        col1, col2 = st.columns(2)

        with col1:
            if st.button("Clock **IN** 🟢", use_container_width=True):
                # PASS DEPARTMENT TO LOGGING FUNCTION
                if log_attendance(worker_id, worker_name, department, "IN"): 
                    st.success(f"**Clocked IN** successfully at **{datetime.now().strftime('%H:%M:%S')}**.")
                # Error handled within log_attendance
        
        with col2:
            if st.button("Clock **OUT** 🔴", use_container_width=True):
                 # PASS DEPARTMENT TO LOGGING FUNCTION
                if log_attendance(worker_id, worker_name, department, "OUT"): 
                    st.success(f"**Clocked OUT** successfully at **{datetime.now().strftime('%H:%M:%S')}**.")
                # Error handled within log_attendance

        st.markdown("---")
        
        if st.button("Log Out"):
            st.session_state['logged_in'] = False
            st.experimental_rerun()


if __name__ == "__main__":
    main()