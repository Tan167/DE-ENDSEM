from __future__ import annotations
import pandas as pd
from datetime import datetime, date
from typing import Tuple
from sqlalchemy.orm import Session

from db.models import Attendance, Task, Employee


def import_attendance_csv(db: Session, file_bytes: bytes) -> Tuple[int, int]:
    """Bulk upsert attendance from CSV with columns: email,date,check_in,check_out,status
    Returns (processed, errors)
    """
    df = pd.read_csv(pd.io.common.BytesIO(file_bytes))
    processed = 0
    errors = 0
    for _, row in df.iterrows():
        try:
            email = str(row.get("email")).strip()
            emp = db.query(Employee).filter(Employee.email == email).one_or_none()
            if not emp:
                errors += 1
                continue
            dt = pd.to_datetime(row.get("date")).date()
            ci = pd.to_datetime(row.get("check_in")) if pd.notna(row.get("check_in")) else None
            co = pd.to_datetime(row.get("check_out")) if pd.notna(row.get("check_out")) else None
            status = str(row.get("status")) if pd.notna(row.get("status")) else None
            att = db.query(Attendance).filter(Attendance.employee_id == emp.employee_id, Attendance.date == dt).one_or_none()
            if not att:
                att = Attendance(employee_id=emp.employee_id, date=dt)
                db.add(att)
            att.check_in = pd.to_datetime(ci).to_pydatetime() if ci is not None else None
            att.check_out = pd.to_datetime(co).to_pydatetime() if co is not None else None
            att.status = status
            processed += 1
        except Exception:
            errors += 1
    db.commit()
    return processed, errors


essential_task_cols = ["email", "task_name", "start_time", "end_time", "status", "productivity_score"]


def import_tasks_csv(db: Session, file_bytes: bytes) -> Tuple[int, int]:
    """Bulk insert/update tasks from CSV with columns: email,task_name,start_time,end_time,status,productivity_score"""
    df = pd.read_csv(pd.io.common.BytesIO(file_bytes))
    processed = 0
    errors = 0
    for _, row in df.iterrows():
        try:
            email = str(row.get("email")).strip()
            emp = db.query(Employee).filter(Employee.email == email).one_or_none()
            if not emp:
                errors += 1
                continue
            start_time = pd.to_datetime(row.get("start_time")) if pd.notna(row.get("start_time")) else None
            end_time = pd.to_datetime(row.get("end_time")) if pd.notna(row.get("end_time")) else None
            status = str(row.get("status")) if pd.notna(row.get("status")) else "Pending"
            pscore = float(row.get("productivity_score")) if pd.notna(row.get("productivity_score")) else None
            from db.models import Task
            t = Task(
                employee_id=emp.employee_id,
                task_name=str(row.get("task_name")),
                start_time=pd.to_datetime(start_time).to_pydatetime() if start_time is not None else None,
                end_time=pd.to_datetime(end_time).to_pydatetime() if end_time is not None else None,
                status=status,
                productivity_score=pscore,
            )
            db.add(t)
            processed += 1
        except Exception:
            errors += 1
    db.commit()
    return processed, errors
