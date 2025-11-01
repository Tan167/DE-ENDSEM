from __future__ import annotations
from datetime import datetime, time, timedelta
from typing import Optional

from config.settings import load_settings

settings = load_settings()


def compute_status(check_in_time: time) -> str:
    """Return Present/Late based on workday start and threshold. Absent is inferred if no check-in exists for a date.
    - Present: check-in <= start + threshold
    - Late: check-in > start + threshold
    """
    start = settings.workday_start
    late_delta = timedelta(minutes=settings.late_threshold_minutes)
    latest_on_time = (datetime.combine(datetime.today(), start) + late_delta).time()
    return "Present" if check_in_time <= latest_on_time else "Late"


def total_work_hours(check_in: Optional[datetime], check_out: Optional[datetime]) -> float:
    if not check_in or not check_out:
        return 0.0
    delta = check_out - check_in
    return round(delta.total_seconds() / 3600.0, 2)


STATUS_TO_VALUE = {"Present": 1.0, "Late": 0.5, "Absent": 0.0}


def status_to_value(status: Optional[str]) -> float:
    return STATUS_TO_VALUE.get(status or "Absent", 0.0)
