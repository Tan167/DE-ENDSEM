from __future__ import annotations
import streamlit as st
from datetime import datetime, date, timedelta
import pandas as pd

from utils import auth
from db.database import SessionLocal
from db import crud
from utils.helpers import total_work_hours


st.set_page_config(page_title="Attendance", page_icon="🕒")

if not auth.require_login():
    st.stop()

user = auth.current_user()

st.title("Attendance Management")

with SessionLocal() as db:
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("Check In", type="primary"):
            record = crud.mark_check_in(db, user["employee_id"], datetime.now())
            st.success(f"Checked in at {record.check_in}")
    with col2:
        if st.button("Check Out"):
            record = crud.mark_check_out(db, user["employee_id"], datetime.now())
            st.success(f"Checked out at {record.check_out}")
    with col3:
        start = st.date_input("Start", value=date.today() - timedelta(days=14))
        end = st.date_input("End", value=date.today())

    st.subheader("My Attendance")
    my_records = crud.list_attendance(db, employee_id=user["employee_id"], start=start, end=end)
    df_my = pd.DataFrame([
        {
            "date": a.date,
            "check_in": a.check_in,
            "check_out": a.check_out,
            "status": a.status,
            "hours": total_work_hours(a.check_in, a.check_out),
        }
        for a in my_records
    ])
    st.dataframe(df_my, width='stretch')

    if auth.is_admin():
        st.divider()
        st.subheader("Admin - Search Attendance")
        emp_list = crud.list_employees(db)
        emp_map = {f"{e.name} ({e.email})": e.employee_id for e in emp_list}
        emp_choice = st.selectbox("Employee", ["All"] + list(emp_map.keys()))
        emp_id = None if emp_choice == "All" else emp_map[emp_choice]
        records = crud.list_attendance(db, employee_id=emp_id, start=start, end=end)
        df_all = pd.DataFrame([
            {
                "employee_id": a.employee_id,
                "date": a.date,
                "check_in": a.check_in,
                "check_out": a.check_out,
                "status": a.status,
                "hours": total_work_hours(a.check_in, a.check_out),
            }
            for a in records
        ])
        st.dataframe(df_all, width='stretch')
