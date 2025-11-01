from __future__ import annotations
import streamlit as st
from datetime import date, datetime, timedelta
import pandas as pd

import os, sys
sys.path.insert(0, os.path.dirname(__file__))

from config.settings import load_settings
from db.database import init_db, SessionLocal
from db import crud
from utils import auth

settings = load_settings()

st.set_page_config(
    page_title="Remote Workforce Attendance and Productivity Monitor",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

init_db()

with open("app/assets/styles.css", "r", encoding="utf-8") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


def render_login():
    st.title("Remote Workforce Attendance and Productivity Monitor")
    st.caption(settings.company_name)

    st.subheader("Login")
    role = st.radio("Role", ["employee", "admin"], horizontal=True)
    email = st.text_input("Email")
    admin_code = st.text_input("Admin Passcode", type="password") if role == "admin" else None
    emp_password = st.text_input("Password", type="password") if role == "employee" else None
    if st.button("Login", type="primary"):
        ok = auth.login(email=email, role=role, passcode=admin_code, password=emp_password)
        if not ok:
            st.error("Login failed. Check email or passcode.")
        else:
            st.rerun()


def render_home():
    user = auth.current_user()
    st.sidebar.title("Navigation")
    st.sidebar.success(f"Logged in: {user['name']} ({user['role']})")
    if st.sidebar.button("Logout"):
        auth.logout(); st.rerun()

    st.header("Welcome 👋")
    st.write("Use the left sidebar to navigate between pages (Dashboard, Attendance, Tasks, Reports, Settings).")


if __name__ == "__main__":
    if not auth.current_user():
        render_login()
    else:
        render_home()
