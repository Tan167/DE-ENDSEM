# Remote Workforce Attendance and Productivity Monitor

A multi-page Streamlit app to monitor remote employees’ attendance, tasks, hours, and productivity with a PostgreSQL backend (SQLAlchemy ORM).

## Features
- Employee Dashboard: attendance, tasks, productivity trend
- Manager Dashboard: team KPIs, department productivity, attendance heatmap, top performers
- Attendance Management: check-in/out, working hours, status detection (Present/Late/Absent)
- Task Management: assign, update, delete tasks with productivity score
- Reports: CSV/PDF export, time-series charts
- Admin: manage employees & departments, CSV bulk upload
- Authentication: simple session-based (admin passcode in `app/config/config.toml`)

## Tech Stack
- Streamlit, Python
- PostgreSQL, SQLAlchemy ORM (psycopg2 driver)
- Plotly, pandas, reportlab

## Setup

1. Configure the database connection in `app/config/config.toml` or set env var `DATABASE_URL`:
   `postgresql+psycopg2://<user>:<password>@<host>:<port>/<dbname>`

2. Install dependencies:

```pwsh
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

3. Run the app:

```pwsh
streamlit run app/app.py
```

4. Login:
- Add yourself as an employee via Settings (Admin), or insert a record in `employees` with your email.
- For admin login, use the passcode from `app/config/config.toml` (default: `admin123`).

## CSV Formats
- Attendance: `email,date,check_in,check_out,status`
- Tasks: `email,task_name,start_time,end_time,status,productivity_score`

## Notes
- This app is for demonstration and internal tools; for production, add proper auth and RBAC.
- The attendance ‘Absent’ status is inferred when a date has no check-in.
