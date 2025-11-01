from __future__ import annotations
from datetime import date, datetime
from typing import Optional

from sqlalchemy import (
    Column,
    Integer,
    String,
    Date,
    DateTime,
    Time,
    ForeignKey,
    Float,
    UniqueConstraint,
    Index,
    func,
)
from sqlalchemy.orm import relationship, Mapped, mapped_column

from db.database import Base


class Department(Base):
    __tablename__ = "departments"

    dept_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    dept_name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    manager_name: Mapped[Optional[str]] = mapped_column(String(100))

    employees = relationship("Employee", back_populates="department")

    def __repr__(self) -> str:
        return f"<Department {self.dept_name}>"


class Employee(Base):
    __tablename__ = "employees"

    employee_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    department_id: Mapped[Optional[int]] = mapped_column(ForeignKey("departments.dept_id"), index=True)
    email: Mapped[str] = mapped_column(String(160), unique=True, nullable=False)
    role: Mapped[str] = mapped_column(String(50), nullable=False, default="employee")
    join_date: Mapped[Optional[date]] = mapped_column(Date)
    password_hash: Mapped[Optional[str]] = mapped_column(String(255))

    department = relationship("Department", back_populates="employees")
    attendance_records = relationship("Attendance", back_populates="employee", cascade="all, delete-orphan")
    tasks = relationship("Task", back_populates="employee", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Employee {self.name} ({self.email})>"


class Attendance(Base):
    __tablename__ = "attendance"

    attendance_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    employee_id: Mapped[int] = mapped_column(ForeignKey("employees.employee_id"), index=True, nullable=False)
    date: Mapped[date] = mapped_column(Date, nullable=False, index=True, default=func.current_date())
    check_in: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    check_out: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    status: Mapped[Optional[str]] = mapped_column(String(20), index=True)

    employee = relationship("Employee", back_populates="attendance_records")

    __table_args__ = (
        UniqueConstraint("employee_id", "date", name="uq_employee_date"),
        Index("ix_attendance_emp_date", "employee_id", "date"),
    )

    def __repr__(self) -> str:
        return f"<Attendance emp={self.employee_id} date={self.date} status={self.status}>"


class Task(Base):
    __tablename__ = "tasks"

    task_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    employee_id: Mapped[int] = mapped_column(ForeignKey("employees.employee_id"), index=True, nullable=False)
    task_name: Mapped[str] = mapped_column(String(200), nullable=False)
    start_time: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    end_time: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="Pending")
    productivity_score: Mapped[Optional[float]] = mapped_column(Float)

    employee = relationship("Employee", back_populates="tasks")

    __table_args__ = (
        Index("ix_tasks_emp_status", "employee_id", "status"),
    )

    def __repr__(self) -> str:
        return f"<Task {self.task_name} emp={self.employee_id} status={self.status}>"
