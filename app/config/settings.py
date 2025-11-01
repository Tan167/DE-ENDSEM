from __future__ import annotations
import os
from dataclasses import dataclass
from datetime import time
from typing import Optional
import toml


CONFIG_PATH = os.path.join(os.path.dirname(__file__), "config.toml")


def _read_config(path: str) -> dict:
    if os.path.exists(path):
        return toml.load(path)
    return {}


@dataclass
class AppSettings:
    database_url: str
    admin_passcode: str
    workday_start: time
    late_threshold_minutes: int
    company_name: str


def load_settings() -> AppSettings:
    cfg = _read_config(CONFIG_PATH)
    db_url = os.environ.get("DATABASE_URL") or cfg.get("database", {}).get("url", "")
    admin_passcode = cfg.get("auth", {}).get("admin_passcode", "admin123")
    company_name = cfg.get("app", {}).get("company_name", "Company")

    workday_start_str = cfg.get("app", {}).get("workday_start", "09:00")
    hh, mm = [int(x) for x in workday_start_str.split(":")] 
    workday_start = time(hh, mm)

    late_threshold_minutes = int(cfg.get("app", {}).get("late_threshold_minutes", 15))

    if not db_url:
        raise RuntimeError(
            "DATABASE_URL not configured. Set env var DATABASE_URL or update app/config/config.toml"
        )

    return AppSettings(
        database_url=db_url,
        admin_passcode=admin_passcode,
        workday_start=workday_start,
        late_threshold_minutes=late_threshold_minutes,
        company_name=company_name,
    )
