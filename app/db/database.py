from __future__ import annotations
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from config.settings import load_settings
from sqlalchemy import inspect, text


settings = load_settings()

engine = create_engine(settings.database_url, pool_pre_ping=True, future=True)

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)


class Base(DeclarativeBase):
    pass


def get_db():
    """FastAPI-style generator for DB sessions (works fine in Streamlit usage too)."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    from db import models  
    Base.metadata.create_all(bind=engine)
    _ensure_optional_columns()


def _ensure_optional_columns():
    """Lightweight migration: add columns if missing.
    Currently ensures employees.password_hash exists.
    """
    try:
        insp = inspect(engine)
        cols = [c.get('name') for c in insp.get_columns('employees')]
        if 'password_hash' not in cols:
            with engine.begin() as conn:
                conn.execute(text('ALTER TABLE employees ADD COLUMN password_hash VARCHAR(255)'))
    except Exception:
        pass
