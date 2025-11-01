from __future__ import annotations
from datetime import date, datetime, timedelta
from typing import List, Optional, Tuple, Dict

import pandas as pd
from sqlalchemy import select, func, and_, or_, update, delete
from sqlalchemy.orm import Session

from config.settings import load_settings
from db.models import Employee, Department, Attendance, Task
from utils.helpers import (
    compute_status,
    total_work_hours,
)
from utils.security import hash_password

settings = load_settings()


# ---------------------- Employees ----------------------

def list_employees(db: Session, department_id: Optional[int] = None) -> List[Employee]:
    stmt = select(Employee).order_by(Employee.name)
    if department_id:
        stmt = stmt.where(Employee.department_id == department_id)
    return list(db.execute(stmt).scalars())


def get_employee_by_email(db: Session, email: str) -> Optional[Employee]:
    stmt = select(Employee).where(Employee.email == email)
    return db.execute(stmt).scalar_one_or_none()


def get_employee(db: Session, employee_id: int) -> Optional[Employee]:
    stmt = select(Employee).where(Employee.employee_id == employee_id)
    return db.execute(stmt).scalar_one_or_none()


def create_employee(db: Session, name: str, email: str, role: str, department_id: Optional[int], join_date: Optional[date], password: Optional[str] = None):
    emp = Employee(name=name, email=email, role=role, department_id=department_id, join_date=join_date)
    if password:
        emp.password_hash = hash_password(password)
    db.add(emp)
    db.commit()
    db.refresh(emp)
    return emp


def update_employee(db: Session, employee_id: int, **kwargs) -> Optional[Employee]:
    emp = get_employee(db, employee_id)
    if not emp:
        return None
    # Handle password separately
    password = kwargs.pop('password', None)
    for k, v in kwargs.items():
        if hasattr(emp, k) and v is not None:
            setattr(emp, k, v)
    if password:
        emp.password_hash = hash_password(password)
    db.commit()
    db.refresh(emp)
    return emp


def delete_employee(db: Session, employee_id: int) -> bool:
    emp = get_employee(db, employee_id)
    if not emp:
        return False
    db.delete(emp)
    db.commit()
    return True


# ---------------------- Departments ----------------------

def list_departments(db: Session) -> List[Department]:
    return list(db.execute(select(Department).order_by(Department.dept_name)).scalars())


def get_department(db: Session, dept_id: int) -> Optional[Department]:
    return db.execute(select(Department).where(Department.dept_id == dept_id)).scalar_one_or_none()


def create_department(db: Session, dept_name: str, manager_name: Optional[str]):
    d = Department(dept_name=dept_name, manager_name=manager_name)
    db.add(d)
    db.commit()
    db.refresh(d)
    return d


def update_department(db: Session, dept_id: int, **kwargs) -> Optional[Department]:
    d = get_department(db, dept_id)
    if not d:
        return None
    for k, v in kwargs.items():
        if hasattr(d, k) and v is not None:
            setattr(d, k, v)
    db.commit(); db.refresh(d)
    return d


def delete_department(db: Session, dept_id: int) -> bool:
    d = get_department(db, dept_id)
    if not d:
        return False
    db.delete(d)
    db.commit()
    return True


# ---------------------- Attendance ----------------------

def get_or_create_attendance(db: Session, employee_id: int, on_date: date) -> Attendance:
    att = db.execute(
        select(Attendance).where(Attendance.employee_id == employee_id, Attendance.date == on_date)
    ).scalar_one_or_none()
    if att:
        return att
    att = Attendance(employee_id=employee_id, date=on_date)
    db.add(att)
    db.commit(); db.refresh(att)
    return att


def mark_check_in(db: Session, employee_id: int, when: datetime) -> Attendance:
    att = get_or_create_attendance(db, employee_id, when.date())
    if not att.check_in:
        att.check_in = when
    att.status = compute_status(when.time())
    db.commit(); db.refresh(att)
    return att


def mark_check_out(db: Session, employee_id: int, when: datetime) -> Attendance:
    att = get_or_create_attendance(db, employee_id, when.date())
    att.check_out = when
    if not att.status:
        att.status = compute_status(att.check_in.time() if att.check_in else when.time())
    db.commit(); db.refresh(att)
    return att


def list_attendance(
    db: Session,
    employee_id: Optional[int] = None,
    start: Optional[date] = None,
    end: Optional[date] = None,
) -> List[Attendance]:
    stmt = select(Attendance).order_by(Attendance.date.desc())
    if employee_id:
        stmt = stmt.where(Attendance.employee_id == employee_id)
    if start:
        stmt = stmt.where(Attendance.date >= start)
    if end:
        stmt = stmt.where(Attendance.date <= end)
    return list(db.execute(stmt).scalars())


def working_hours_timeseries(db: Session, employee_id: Optional[int], start: date, end: date) -> pd.DataFrame:
    records = list_attendance(db, employee_id, start, end)
    rows = []
    for r in records:
        hours = total_work_hours(r.check_in, r.check_out)
        rows.append({"date": r.date, "employee_id": r.employee_id, "hours": hours})
    df = pd.DataFrame(rows)
    if df.empty:
        return df
    df = df.sort_values("date")
    return df


# ---------------------- Tasks ----------------------

def list_tasks(
    db: Session,
    employee_id: Optional[int] = None,
    status: Optional[str] = None,
    start: Optional[datetime] = None,
    end: Optional[datetime] = None,
) -> List[Task]:
    stmt = select(Task).order_by(Task.start_time.desc().nullslast())
    if employee_id:
        stmt = stmt.where(Task.employee_id == employee_id)
    if status:
        stmt = stmt.where(Task.status == status)
    if start:
        stmt = stmt.where(Task.start_time >= start)
    if end:
        stmt = stmt.where(Task.end_time <= end)
    return list(db.execute(stmt).scalars())


def create_task(
    db: Session,
    employee_id: int,
    task_name: str,
    start_time: Optional[datetime],
    end_time: Optional[datetime],
    status: str = "Pending",
    productivity_score: Optional[float] = None,
) -> Task:
    t = Task(
        employee_id=employee_id,
        task_name=task_name,
        start_time=start_time,
        end_time=end_time,
        status=status,
        productivity_score=productivity_score,
    )
    db.add(t)
    db.commit(); db.refresh(t)
    return t


def update_task(db: Session, task_id: int, **kwargs) -> Optional[Task]:
    t = db.get(Task, task_id)
    if not t:
        return None
    for k, v in kwargs.items():
        if hasattr(t, k) and v is not None:
            setattr(t, k, v)
    db.commit(); db.refresh(t)
    return t


def delete_task(db: Session, task_id: int) -> bool:
    t = db.get(Task, task_id)
    if not t:
        return False
    db.delete(t)
    db.commit()
    return True


# ---------------------- Analytics ----------------------

def department_productivity(db: Session, start: Optional[date] = None, end: Optional[date] = None) -> pd.DataFrame:
    """Average productivity score by department."""
    stmt = (
        select(Department.dept_name, func.avg(Task.productivity_score))
        .join(Employee, Employee.department_id == Department.dept_id)
        .join(Task, Task.employee_id == Employee.employee_id)
        .group_by(Department.dept_name)
        .order_by(Department.dept_name)
    )
    if start:
        stmt = stmt.where(Task.start_time >= datetime.combine(start, datetime.min.time()))
    if end:
        stmt = stmt.where(Task.end_time <= datetime.combine(end, datetime.max.time()))
    rows = db.execute(stmt).all()
    return pd.DataFrame(rows, columns=["department", "avg_productivity"])


def top_performers(db: Session, limit: int = 5, start: Optional[date] = None, end: Optional[date] = None) -> pd.DataFrame:
    stmt = (
        select(Employee.name, func.avg(Task.productivity_score).label("avg_score"))
        .join(Task, Task.employee_id == Employee.employee_id)
        .group_by(Employee.name)
        .order_by(func.avg(Task.productivity_score).desc())
        .limit(limit)
    )
    if start:
        stmt = stmt.where(Task.start_time >= datetime.combine(start, datetime.min.time()))
    if end:
        stmt = stmt.where(Task.end_time <= datetime.combine(end, datetime.max.time()))
    rows = db.execute(stmt).all()
    return pd.DataFrame(rows, columns=["employee", "avg_score"])


def attendance_summary(db: Session, start: date, end: date, department_id: Optional[int] = None) -> pd.DataFrame:
    stmt = (
        select(Attendance.employee_id, Attendance.date, Attendance.status)
        .join(Employee, Employee.employee_id == Attendance.employee_id)
        .where(and_(Attendance.date >= start, Attendance.date <= end))
    )
    if department_id:
        stmt = stmt.where(Employee.department_id == department_id)
    rows = db.execute(stmt).all()
    return pd.DataFrame(rows, columns=["employee_id", "date", "status"])


def daily_average_productivity(db: Session, employee_id: Optional[int], start: date, end: date) -> pd.DataFrame:
    stmt = (
        select(func.date_trunc('day', Task.end_time).label("day"), func.avg(Task.productivity_score))
        .where(Task.productivity_score.is_not(None))
        .group_by(func.date_trunc('day', Task.end_time))
        .order_by(func.date_trunc('day', Task.end_time))
    )
    if employee_id:
        stmt = stmt.where(Task.employee_id == employee_id)
    if start:
        stmt = stmt.where(Task.end_time >= datetime.combine(start, datetime.min.time()))
    if end:
        stmt = stmt.where(Task.end_time <= datetime.combine(end, datetime.max.time()))
    rows = db.execute(stmt).all()
    return pd.DataFrame(rows, columns=["day", "avg_productivity"])