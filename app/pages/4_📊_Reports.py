from __future__ import annotations
import streamlit as st
from datetime import date, timedelta
import pandas as pd

from utils import auth
from db.database import SessionLocal
from db import crud
from utils.reports import generate_pdf_report, df_to_csv_bytes
from utils.charts import work_hours_timeseries
from utils.csv_utils import import_attendance_csv, import_tasks_csv


st.set_page_config(page_title="Reports", page_icon="📊")

if not auth.require_login():
    st.stop()

user = auth.current_user()

st.title("Reports & Exports")

with SessionLocal() as db:
    col1, col2, col3 = st.columns(3)
    with col1:
        start = st.date_input("Start Date", value=date.today() - timedelta(days=30))
    with col2:
        end = st.date_input("End Date", value=date.today())
    with col3:
        emp_filter = None
        if user["role"] == "admin":
            emps = {f"{e.name} ({e.email})": e.employee_id for e in crud.list_employees(db)}
            emp_choice = st.selectbox("Employee (optional)", ["All"] + list(emps.keys()))
            emp_filter = None if emp_choice == "All" else emps[emp_choice]

    # KPIs
    st.subheader("KPIs")
    df_dept = crud.department_productivity(db, start=start, end=end)
    df_top = crud.top_performers(db, start=start, end=end)
    total_tasks = len(crud.list_tasks(db, employee_id=emp_filter))
    kpi_cols = st.columns(3)
    kpi_cols[0].metric("Departments", len(df_dept))
    kpi_cols[1].metric("Top Performers Listed", len(df_top))
    kpi_cols[2].metric("Total Tasks", total_tasks)

    # Time Series of Hours
    df_hours = crud.working_hours_timeseries(db, employee_id=emp_filter, start=start, end=end)
    st.plotly_chart(work_hours_timeseries(df_hours), use_container_width=True)

    # Export section
    st.subheader("Export Data")
    tab1, tab2 = st.tabs(["CSV", "PDF"])
    with tab1:
        st.caption("Download key data as CSV")
        btn1 = st.download_button(
            "Download Department Productivity", data=df_to_csv_bytes(df_dept), file_name="dept_productivity.csv", mime="text/csv"
        )
        btn2 = st.download_button(
            "Download Top Performers", data=df_to_csv_bytes(df_top), file_name="top_performers.csv", mime="text/csv"
        )
    with tab2:
        st.caption("Generate a printable PDF report")
        pdf = generate_pdf_report(
            title="Team Report",
            kpis={
                "Departments": str(len(df_dept)),
                "Top Performers": str(len(df_top)),
                "Total Tasks": str(total_tasks),
            },
            sections={
                "Department Productivity": df_dept,
                "Top Performers": df_top,
            },
        )
        st.download_button("Download PDF", data=pdf, file_name="report.pdf", mime="application/pdf")

    if auth.is_admin():
        st.divider()
        st.subheader("Admin: Bulk Upload via CSV")
        st.markdown("- Attendance CSV columns: email,date,check_in,check_out,status")
        st.markdown("- Tasks CSV columns: email,task_name,start_time,end_time,status,productivity_score")
        c1, c2 = st.columns(2)
        with c1:
            up1 = st.file_uploader("Upload Attendance CSV", type=["csv"])
            if up1 is not None:
                processed, errors = import_attendance_csv(db, up1.getvalue())
                st.success(f"Attendance import complete. Processed={processed}, Errors={errors}")
        with c2:
            up2 = st.file_uploader("Upload Tasks CSV", type=["csv"], key="tasks_csv")
            if up2 is not None:
                processed, errors = import_tasks_csv(db, up2.getvalue())
                st.success(f"Tasks import complete. Processed={processed}, Errors={errors}")
