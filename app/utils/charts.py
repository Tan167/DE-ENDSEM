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
