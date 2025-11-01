from __future__ import annotations
import streamlit as st
from datetime import date, timedelta
import pandas as pd

from utils import auth
from db.database import SessionLocal
from db import crud
from utils.charts import productivity_trend, attendance_heatmap, dept_productivity_pie


st.set_page_config(page_title="Dashboard", page_icon="🏠")

if not auth.require_login():
    st.stop()

user = auth.current_user()

st.title("Dashboard")

colf1, colf2, colf3 = st.columns(3)
with colf1:
    start = st.date_input("Start Date", value=date.today() - timedelta(days=30))
with colf2:
    end = st.date_input("End Date", value=date.today())
with colf3:
    if auth.is_admin():
        dept_filter = st.text_input("Filter by Department (name contains)", value="")
    else:
        dept_filter = ""

with SessionLocal() as db:
    if user["role"] != "admin":
        st.subheader("Your Productivity Trend")
        df_prod = crud.daily_average_productivity(db, employee_id=user["employee_id"], start=start, end=end)
        fig = productivity_trend(df_prod)
        st.plotly_chart(fig, use_container_width=True)

        st.subheader("Recent Attendance")
        att = crud.list_attendance(db, employee_id=user["employee_id"], start=start, end=end)
        df_att = pd.DataFrame([
            {
                "date": a.date,
                "check_in": a.check_in,
                "check_out": a.check_out,
                "status": a.status,
            }
            for a in att
        ])
        st.dataframe(df_att, use_container_width=True)

        st.subheader("Your Tasks")
        tasks = crud.list_tasks(db, employee_id=user["employee_id"]) 
        df_tasks = pd.DataFrame([
            {
                "task_id": t.task_id,
                "task_name": t.task_name,
                "status": t.status,
                "start_time": t.start_time,
                "end_time": t.end_time,
                "productivity_score": t.productivity_score,
            }
            for t in tasks
        ])
        if not df_tasks.empty:
            df_tasks["progress"] = df_tasks["status"].map({"Completed": 1.0, "In Progress": 0.5, "Pending": 0.1}).fillna(0.0)
        st.dataframe(df_tasks, use_container_width=True)

    else:
        st.subheader("Department Productivity")
        df_dept = crud.department_productivity(db, start=start, end=end)
        if dept_filter:
            df_dept = df_dept[df_dept["department"].str.contains(dept_filter, case=False, na=False)]
        st.plotly_chart(dept_productivity_pie(df_dept), use_container_width=True)


        st.subheader("Top Performers")
        df_top = crud.top_performers(db, limit=5, start=start, end=end)
        st.dataframe(df_top, use_container_width=True)

        st.subheader("Alerts")
        today = date.today()
        all_emps = crud.list_employees(db)
        missing = []
        for e in all_emps:
            recs = crud.list_attendance(db, employee_id=e.employee_id, start=today, end=today)
            if not recs or not recs[0].check_in:
                missing.append(e.name)
        if missing:
            st.warning(f"Missing check-in today: {', '.join(missing[:10])}{' ...' if len(missing)>10 else ''}")

        df_prod7 = crud.daily_average_productivity(db, employee_id=None, start=today - timedelta(days=7), end=today)
        if not df_prod7.empty and df_prod7['avg_productivity'].mean() < 50:
            st.error("Average productivity last 7 days is below 50.")
