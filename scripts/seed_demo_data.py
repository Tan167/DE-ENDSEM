from __future__ import annotations
import os
import sys
import random
from datetime import datetime, date, timedelta, time

# Ensure app/ modules are importable
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
APP_DIR = os.path.join(PROJECT_ROOT, "app")
if APP_DIR not in sys.path:
    sys.path.insert(0, APP_DIR)

from db.database import SessionLocal, init_db  # type: ignore
from db import crud  # type: ignore
from db.models import Department, Employee  # type: ignore


DEPARTMENTS = [
    ("Engineering", "Rakesh Kumar"),
    ("Sales", "Pooja Mehta"),
    ("HR", "Vivek Kapoor"),
    ("Finance", "Neha Sharma"),
    ("Operations", "Arjun Singh"),
    ("Marketing", "Ishita Desai"),
    ("Support", "Rahul Nair"),
]

INDIAN_EMPLOYEES = [
    "Aarav Sharma",
    "Vihaan Iyer",
    "Isha Patel",
    "Ananya Gupta",
    "Rohan Verma",
    "Priya Nair",
    "Kabir Singh",
    "Meera Joshi",
    "Aditya Rao",
    "Sneha Menon",
]

DEFAULT_PASSWORD = "Pass@123"


def month_range_of_previous_ref(today: date) -> tuple[date, date]:
    first_this_month = today.replace(day=1)
    last_prev_month = first_this_month - timedelta(days=1)
    first_prev_month = last_prev_month.replace(day=1)
    return first_prev_month, last_prev_month


def ensure_departments(db) -> list[Department]:
    existing = {d.dept_name: d for d in crud.list_departments(db)}
    created = []
    for name, manager in DEPARTMENTS:
        if name in existing:
            created.append(existing[name])
        else:
            d = crud.create_department(db, name, manager)
            created.append(d)
    return created


def sanitize_email(name: str) -> str:
    base = name.lower().replace(" ", ".")
    return f"{base}@acme.test"


def ensure_employees(db, departments: list[Department]) -> list[Employee]:
    # Rotate departments while creating employees
    emps = []
    for idx, name in enumerate(INDIAN_EMPLOYEES):
        email = sanitize_email(name)
        existing = crud.get_employee_by_email(db, email)
        dept = departments[idx % len(departments)] if departments else None
        if existing:
            emps.append(existing)
        else:
            e = crud.create_employee(
                db,
                name=name,
                email=email,
                role="employee",
                department_id=dept.dept_id if dept else None,
                join_date=date.today() - timedelta(days=60),
                password=DEFAULT_PASSWORD,
            )
            emps.append(e)
    return emps


def is_weekday(d: date) -> bool:
    return d.weekday() < 5  # 0=Mon, 6=Sun


def random_checkin_out(on_date: date) -> tuple[datetime, datetime]:
    # Check-in between 09:00 and 10:15, checkout between 17:30 and 19:30
    cin_hour = 9 + random.randint(0, 1)
    cin_min = random.choice([0, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55])
    if cin_hour == 10:
        cin_min = random.choice([0, 5, 10, 15])
    cout_hour = random.choice([17, 18, 19])
    cout_min = random.choice([0, 10, 20, 30, 40, 50])
    ci = datetime.combine(on_date, time(cin_hour, cin_min))
    co = datetime.combine(on_date, time(cout_hour, cout_min))
    if co <= ci:
        co = ci + timedelta(hours=8, minutes=random.choice([0, 15, 30, 45]))
    return ci, co


def seed_attendance_last_month(db, employees: list[Employee], target_entries: int = 150):
    today = date.today()
    start, end = month_range_of_previous_ref(today)
    days = []
    d = start
    while d <= end:
        if is_weekday(d):
            days.append(d)
        d += timedelta(days=1)

    # Probability tuned to achieve roughly target_entries
    # expected = len(employees) * len(days) * p ~= target
    total_slots = max(1, len(employees) * len(days))
    p = min(0.95, max(0.1, target_entries / total_slots))

    created = 0
    for emp in employees:
        for day in days:
            if random.random() <= p:
                ci, co = random_checkin_out(day)
                crud.mark_check_in(db, emp.employee_id, ci)
                crud.mark_check_out(db, emp.employee_id, co)
                created += 1
    return created


def main():
    init_db()
    with SessionLocal() as db:
        depts = ensure_departments(db)
        emps = ensure_employees(db, depts)
        made = seed_attendance_last_month(db, emps, target_entries=150)
        print(f"Seeded departments={len(depts)}, employees={len(emps)}, attendance entries~={made}")


if __name__ == "__main__":
    random.seed(205)  # deterministic-ish
    main()
