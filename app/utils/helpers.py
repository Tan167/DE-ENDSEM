from __future__ import annotations
from datetime import datetime, time, timedelta
from typing import Optional

from config.settings import load_settings

_settings = load_settings()


def _parse_workday_start(s: str) -> time:
    try:
        hh, mm = s.split(":", 1)
        return time(int(hh), int(mm))
    except Exception:
        return time(9, 0)


def compute_status(check_in_time: Optional[time]) -> str:
    """Return a simple attendance status based on check-in time.

    - On Time: check-in <= workday_start + late_threshold
    - Late:    check-in >  workday_start + late_threshold
    - Unknown: no check-in provided
    """
    if not check_in_time:
        return "Unknown"
    start = _parse_workday_start(_settings.workday_start)
    threshold = (datetime.combine(datetime.today().date(), start) + timedelta(minutes=_settings.late_threshold_minutes)).time()
    return "On Time" if check_in_time <= threshold else "Late"


def total_work_hours(check_in: Optional[datetime], check_out: Optional[datetime]) -> float:
    if not check_in or not check_out:
        return 0.0
    delta = check_out - check_in
    return max(delta.total_seconds() / 3600.0, 0.0)


def status_to_value(status: Optional[str]) -> float:
    """Map attendance status to numeric scale for visualization.
    Unknown -> 0.1, Late -> 0.5, On Time -> 1.0
    """
    if not status:
        return 0.1
    s = str(status).lower()
    if "on" in s and "time" in s:
        return 1.0
    if "late" in s:
        return 0.5
    return 0.1
