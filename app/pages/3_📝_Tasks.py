from __future__ import annotations
import streamlit as st
from datetime import datetime
import pandas as pd

from utils import auth
from db.database import SessionLocal
from db import crud


st.set_page_config(page_title="Tasks", page_icon="📝")

if not auth.require_login():
    st.stop()

user = auth.current_user()

st.title("Tasks")

with SessionLocal() as db:
    if user["role"] == "admin":
        st.subheader("Assign New Task")
        emp_list = crud.list_employees(db)
        emp_map = {f"{e.name} ({e.email})": e.employee_id for e in emp_list}
        emp_choice = st.selectbox("Employee", list(emp_map.keys()))
        employee_id = emp_map[emp_choice]
        task_name = st.text_input("Task Name")

        def datetime_picker(label: str):
            use_dt = st.checkbox(f"Set {label}", value=False, key=f"use_{label}")
            if not use_dt:
                return None
            c1, c2 = st.columns(2)
            with c1:
                d = st.date_input(f"{label} - Date")
            with c2:
                t = st.time_input(f"{label} - Time", value=datetime.now().time())
            return datetime.combine(d, t) if d and t else None

        col1, col2 = st.columns(2)
        with col1:
            start_time = datetime_picker("Start Time")
        with col2:
            end_time = datetime_picker("End Time")
        status = st.selectbox("Status", ["Pending", "In Progress", "Completed"])
        pscore = st.number_input("Productivity Score", min_value=0.0, max_value=100.0, value=0.0)
        if st.button("Create Task", type="primary"):
            crud.create_task(db, employee_id, task_name, start_time, end_time, status, pscore)
            st.success("Task created.")

    st.subheader("My Tasks" if user["role"] != "admin" else "All Tasks")
    employee_id = user["employee_id"] if user["role"] != "admin" else None
    tasks = crud.list_tasks(db, employee_id=employee_id)
    df = pd.DataFrame([
        {
            "task_id": t.task_id,
            "employee_id": t.employee_id,
            "task_name": t.task_name,
            "status": t.status,
            "start_time": t.start_time,
            "end_time": t.end_time,
            "productivity_score": t.productivity_score,
        }
        for t in tasks
    ])
    st.dataframe(df, use_container_width=True)

    st.subheader("Update Task")
    if not df.empty:
        task_ids = df["task_id"].tolist()
        t_id = st.selectbox("Task ID", task_ids)
        new_status = st.selectbox("New Status", ["Pending", "In Progress", "Completed"])    
        new_pscore = st.number_input("Productivity Score", min_value=0.0, max_value=100.0, value=0.0)
        if st.button("Update", type="primary"):
            crud.update_task(db, t_id, status=new_status, productivity_score=new_pscore)
            st.success("Task updated.")

    if user["role"] == "admin":
        st.subheader("Delete Task")
        if not df.empty:
            t_id2 = st.selectbox("Task ID to Delete", df["task_id"].tolist(), key="del")
            if st.button("Delete", type="secondary"):
                crud.delete_task(db, t_id2)
                st.warning("Task deleted.")
