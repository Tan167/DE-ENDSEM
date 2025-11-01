from __future__ import annotations
from dataclasses import dataclass
import os
from pathlib import Path
import toml


@dataclass
class Settings:
    database_url: str
    admin_passcode: str
    workday_start: str
    late_threshold_minutes: int
    company_name: str


def _read_toml(path: Path) -> dict:
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as f:
        return toml.load(f)


def load_settings() -> Settings:
    """Load application settings from config.toml with environment overrides.

    Environment overrides:
      - DATABASE_URL -> database.url
      - ADMIN_PASSCODE -> auth.admin_passcode
      - COMPANY_NAME -> app.company_name
    """
    here = Path(__file__).resolve().parent
    cfg = _read_toml(here / "config.toml")

    # Fetch values with sensible fallbacks
    db_url = os.getenv("DATABASE_URL") or cfg.get("database", {}).get("url", "")
    admin_pass = os.getenv("ADMIN_PASSCODE") or cfg.get("auth", {}).get("admin_passcode", "admin123")
    workday_start = cfg.get("app", {}).get("workday_start", "09:00")
    late_threshold = int(cfg.get("app", {}).get("late_threshold_minutes", 15))
    company_name = os.getenv("COMPANY_NAME") or cfg.get("app", {}).get("company_name", "Company")

    return Settings(
        database_url=db_url,
        admin_passcode=admin_pass,
        workday_start=workday_start,
        late_threshold_minutes=late_threshold,
        company_name=company_name,
    )
