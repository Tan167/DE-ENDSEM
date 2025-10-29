import streamlit as st
from pymongo import MongoClient
from datetime import datetime
import pandas as pd



MONGO_URI = "mongodb://localhost:27017"
DB_NAME = "AttendanceDB"
COLLECTION_NAME = "remote_logs"

@st.cache_resource
def get_mongo_client():
    
    
    client = MongoClient(MONGO_URI)
    return client



def log_attendance(worker_id, worker_name, department, status):
    """Inserts an attendance record (including department) into MongoDB."""
    try:
        client = get_mongo_client()
        db = client[DB_NAME]
        collection = db[COLLECTION_NAME]

        log_entry = {
            "worker_id": worker_id,
            "worker_name": worker_name,
            "department": department,  
            "timestamp": datetime.now(),
            "status": status, 
            "date": datetime.now().date().isoformat()
        }
        result = collection.insert_one(log_entry)
        return result.acknowledged
    except Exception as e:
        st.error(f"Database error: {e}")
        return False


def main():
    st.set_page_config(page_title="Remote Attendance System", layout="centered")
    st.title("👨‍💻 Remote Worker Attendance System")

    
    if 'logged_in' not in st.session_state:
        st.session_state['logged_in'] = False
        st.session_state['worker_id'] = None
        st.session_state['worker_name'] = None
        st.session_state['department'] = None  

    if not st.session_state['logged_in']:
        st.header("Login")
        
        
        worker_id_input = st.text_input("Worker ID (e.g., RMT-001)")
        worker_name_input = st.text_input("Full Name")
        
        
        departments = ["HR", "IT", "Sales", "Admin", "Management"]
        department_select = st.selectbox(
            "Select Department", 
            options=departments, 
            index=0 
        )
        
        if st.button("Log In", use_container_width=True):
            if worker_id_input and worker_name_input and department_select:
                st.session_state['logged_in'] = True
                st.session_state['worker_id'] = worker_id_input.upper().strip()
                st.session_state['worker_name'] = worker_name_input.strip()
                st.session_state['department'] = department_select 
                st.experimental_rerun() 
            else:
                st.error("Please enter Worker ID, Full Name, and select a Department.")
    
    else:
        
        worker_id = st.session_state['worker_id']
        worker_name = st.session_state['worker_name']
        department = st.session_state['department'] 

        st.success(f"Welcome, **{worker_name}** ({worker_id}) from **{department}**")
        st.subheader("Mark Your Attendance")
        st.markdown(f"Current Time: **{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}**")

        col1, col2 = st.columns(2)

        with col1:
            if st.button("Clock **IN** 🟢", use_container_width=True):
                
                if log_attendance(worker_id, worker_name, department, "IN"): 
                    st.success(f"**Clocked IN** successfully at **{datetime.now().strftime('%H:%M:%S')}**.")
                
        
        with col2:
            if st.button("Clock **OUT** 🔴", use_container_width=True):
                 
                if log_attendance(worker_id, worker_name, department, "OUT"): 
                    st.success(f"**Clocked OUT** successfully at **{datetime.now().strftime('%H:%M:%S')}**.")
                

        st.markdown("---")
        
        if st.button("Log Out"):
            st.session_state['logged_in'] = False
            st.experimental_rerun()


if __name__ == "__main__":
    main()