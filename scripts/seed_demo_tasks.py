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
from db.models import Employee  # type: ignore


def month_range_of_previous_ref(today: date) -> tuple[date, date]:
    first_this_month = today.replace(day=1)
    last_prev_month = first_this_month - timedelta(days=1)
    first_prev_month = last_prev_month.replace(day=1)
    return first_prev_month, last_prev_month


def random_task_times(on_date: date) -> tuple[datetime | None, datetime | None]:
    # Randomly choose a start within working hours and add 1-6 hours for end
    start_hour = random.choice([9, 10, 11, 12, 13, 14, 15])
    start_min = random.choice([0, 15, 30, 45])
    start_dt = datetime.combine(on_date, time(start_hour, start_min))
    duration_hours = random.randint(1, 6)
    end_dt = start_dt + timedelta(hours=duration_hours)
    return start_dt, end_dt


def pick_status_and_score() -> tuple[str, float | None]:
    # Weighted statuses
    status = random.choices(["Completed", "In Progress", "Pending"], weights=[0.55, 0.3, 0.15], k=1)[0]
    if status == "Completed":
        score = round(random.uniform(60, 100), 1)
    elif status == "In Progress":
        score = round(random.uniform(30, 75), 1)
    else:
        score = None
    return status, score


def seed_tasks_last_month(db, total_tasks: int = 50):
    emps = crud.list_employees(db)
    if not emps:
        print("No employees found. Seed employees first.")
        return 0
    start, end = month_range_of_previous_ref(date.today())
    all_days = []
    d = start
    while d <= end:
        if d.weekday() < 5:
            all_days.append(d)
        d += timedelta(days=1)

    created = 0
    for i in range(total_tasks):
        emp = emps[i % len(emps)]
        on_day = random.choice(all_days)
        st_dt, en_dt = random_task_times(on_day)
        status, score = pick_status_and_score()
        # Pending tasks may not have an end time
        end_time = en_dt if status != "Pending" else None
        task_name = f"Monthly Task #{i+1}"
        crud.create_task(
            db,
            employee_id=emp.employee_id,
            task_name=task_name,
            start_time=st_dt,
            end_time=end_time,
            status=status,
            productivity_score=score,
        )
        created += 1
    return created


def main():
    init_db()
    with SessionLocal() as db:
        made = seed_tasks_last_month(db, total_tasks=50)
        print(f"Seeded tasks created={made}")


if __name__ == "__main__":
    random.seed(305)
    main()
