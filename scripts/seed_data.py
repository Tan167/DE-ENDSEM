from __future__ import annotations
import os
import sys
from datetime import date

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
APP_DIR = os.path.join(PROJECT_ROOT, "app")
if APP_DIR not in sys.path:
    sys.path.insert(0, APP_DIR)

from db.database import SessionLocal, init_db
from db import crud


def main():
    init_db()
    with SessionLocal() as db:
        # Ensure at least one department
        deps = crud.list_departments(db)
        if not deps:
            d = crud.create_department(db, "General", "Admin")
            print("Created department 'General'.")
        else:
            d = deps[0]

        # Seed an admin user for first login
        admin_email = "admin@acme.test"
        existing = crud.get_employee_by_email(db, admin_email)
        if not existing:
            crud.create_employee(db, name="Admin User", email=admin_email, role="admin", department_id=d.dept_id, join_date=date.today())
            print(f"Created admin user: {admin_email}")
        else:
            print(f"Admin user already exists: {admin_email}")


if __name__ == "__main__":
    main()
