from __future__ import annotations
from typing import Optional
import pandas as pd
import plotly.express as px

from utils.helpers import status_to_value


def productivity_trend(df_daily: pd.DataFrame, title: str = "Daily Productivity"):
    if df_daily.empty:
        return px.line(title=title)
    fig = px.line(df_daily, x="day", y="avg_productivity", markers=True, title=title)
    fig.update_layout(yaxis_title="Avg Productivity", xaxis_title="Date")
    return fig


def attendance_heatmap(df_att: pd.DataFrame, employees_map: Optional[dict] = None, title: str = "Attendance Heatmap"):
    # Expect columns: employee_id, date, status
    if df_att.empty:
        return px.imshow([[0]], labels=dict(color="Status"), title=title)
    df = df_att.copy()
    df["value"] = df["status"].map(status_to_value)
    if employees_map:
        df["employee"] = df["employee_id"].map(employees_map)
    else:
        df["employee"] = df["employee_id"].astype(str)
    pivot = df.pivot_table(index="employee", columns="date", values="value", aggfunc="mean", fill_value=0)
    fig = px.imshow(
        pivot.values,
        x=pivot.columns.astype(str),
        y=pivot.index,
        color_continuous_scale=["#fca5a5", "#fcd34d", "#86efac"],
        title=title,
        aspect="auto",
    )
    fig.update_coloraxes(colorbar_title="Status")
    return fig


def dept_productivity_pie(df: pd.DataFrame, title: str = "Department Productivity"):
    if df.empty:
        return px.pie(title=title)
    return px.pie(df, names="department", values="avg_productivity", title=title, hole=0.3)


def work_hours_timeseries(df_hours: pd.DataFrame, title: str = "Work Hours"):
    if df_hours.empty:
        return px.line(title=title)
    fig = px.line(df_hours, x="date", y="hours", color="employee_id", markers=True, title=title)
    fig.update_layout(yaxis_title="Hours", xaxis_title="Date")
    return fig
