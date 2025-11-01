from __future__ import annotations
import streamlit as st
from datetime import date
import pandas as pd

from utils import auth
from db.database import SessionLocal
from db import crud


st.set_page_config(page_title="Settings", page_icon="⚙️")

if not auth.require_login():
    st.stop()

if not auth.is_admin():
    st.error("Admin access required.")
    st.stop()

st.title("Admin Settings")

with SessionLocal() as db:
    st.subheader("Departments")
    with st.expander("Create Department"):
        dept_name = st.text_input("Department Name", key="create_dept_name")
        manager_name = st.text_input("Manager Name", key="create_dept_manager")
        if st.button("Add Department", type="primary", key="btn_add_department"):
            if dept_name:
                crud.create_department(db, dept_name, manager_name)
                st.success("Department created.")

    deps = crud.list_departments(db)
    df_deps = pd.DataFrame([{ "dept_id": d.dept_id, "dept_name": d.dept_name, "manager_name": d.manager_name } for d in deps])
    st.dataframe(df_deps, width='stretch')

    st.divider()

    st.subheader("Employees")
    with st.expander("Add Employee"):
        name = st.text_input("Name", key="create_emp_name")
        email = st.text_input("Email", key="create_emp_email")
        role = st.selectbox("Role", ["employee", "admin"], key="create_emp_role") 
        dep_map = {d.dept_name: d.dept_id for d in deps}
        dept_name_sel = st.selectbox("Department", ["None"] + list(dep_map.keys()), key="create_emp_department")
        dept_id = None if dept_name_sel == "None" else dep_map[dept_name_sel]
        jdate = st.date_input("Join Date", value=date.today(), key="create_emp_join_date")
        password = st.text_input("Initial Password (employee login)", type="password", key="create_emp_password")
        if st.button("Create Employee", type="primary", key="btn_create_employee"):
            crud.create_employee(db, name=name, email=email, role=role, department_id=dept_id, join_date=jdate, password=password if password else None)
            st.success("Employee created.")

    emps = crud.list_employees(db)
    df_emps = pd.DataFrame([
        {
            "employee_id": e.employee_id,
            "name": e.name,
            "email": e.email,
            "role": e.role,
            "department_id": e.department_id,
            "join_date": e.join_date,
        }
        for e in emps
    ])
    st.dataframe(df_emps, width='stretch')

    st.subheader("Edit/Delete Employee")
    if not df_emps.empty:
        emp_ids = df_emps["employee_id"].tolist()
        eid = st.selectbox("Employee ID", emp_ids, key="edit_emp_select")
        e = next((x for x in emps if x.employee_id == eid), None)
        if e:
            col1, col2 = st.columns(2)
            with col1:
                name2 = st.text_input("Name", value=e.name, key=f"edit_emp_name_{eid}")
                role2 = st.selectbox("Role", ["employee", "admin"], index=1 if e.role=="admin" else 0, key=f"edit_emp_role_{eid}")
            with col2:
                email2 = st.text_input("Email", value=e.email, key=f"edit_emp_email_{eid}")
                dept2 = st.selectbox("Department", ["None"] + list(dep_map.keys()), index=(list(dep_map.keys()).index(next((k for k,v in dep_map.items() if v==e.department_id), None)) + 1) if e.department_id else 0, key=f"edit_emp_department_{eid}")
                dept_id2 = None if dept2 == "None" else dep_map[dept2]
            new_password = st.text_input("Reset Password (leave blank to keep)", type="password", key=f"edit_emp_password_{eid}")
            if st.button("Save Changes", type="primary", key=f"btn_save_emp_{eid}"):
                crud.update_employee(db, eid, name=name2, email=email2, role=role2, department_id=dept_id2, password=new_password if new_password else None)
                st.success("Employee updated.")
            if st.button("Delete Employee", type="secondary", key=f"btn_delete_emp_{eid}"):
                crud.delete_employee(db, eid)
                st.warning("Employee deleted.")
