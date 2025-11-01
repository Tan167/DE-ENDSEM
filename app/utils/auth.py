from __future__ import annotations
import streamlit as st
from typing import Optional

from db.crud import get_employee_by_email
from db.database import SessionLocal
from config.settings import load_settings
from utils.security import verify_password

settings = load_settings()


SESSION_KEY = "auth_user"


def login(email: str, role: str, passcode: Optional[str] = None, password: Optional[str] = None) -> bool:
    with SessionLocal() as db:
        user = get_employee_by_email(db, email)
        if not user:
            return False
        if role == "admin":
            if passcode != settings.admin_passcode:
                return False
        # Employee role requires password verification
        if role == "employee":
            if user.role not in ("employee", "admin"):
                return False
            if not password or not verify_password(password, user.password_hash):
                return False
        st.session_state[SESSION_KEY] = {
            "employee_id": user.employee_id,
            "name": user.name,
            "email": user.email,
            "role": role if role == "admin" else user.role,
            "department_id": user.department_id,
        }
        return True


def logout():
    if SESSION_KEY in st.session_state:
        del st.session_state[SESSION_KEY]


def current_user() -> Optional[dict]:
    return st.session_state.get(SESSION_KEY)


def require_login():
    user = current_user()
    if not user:
        st.warning("Please log in to continue.")
        return False
    return True


def is_admin() -> bool:
    u = current_user()
    return bool(u and u.get("role") == "admin")
