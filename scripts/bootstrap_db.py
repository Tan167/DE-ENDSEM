from __future__ import annotations
import os
import sys
import urllib.parse as up

import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

# Add the app directory to sys.path so we can import modules as top-level (config, db, utils)
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
APP_DIR = os.path.join(PROJECT_ROOT, "app")
if APP_DIR not in sys.path:
    sys.path.insert(0, APP_DIR)
from config.settings import load_settings  # noqa: E402


def ensure_database_exists():
    settings = load_settings()
    db_url = settings.database_url
    # Parse URL to get connection details
    # db_url format: postgresql+psycopg2://user:pass@host:port/dbname
    if db_url.startswith("postgresql+"):
        pg_url = db_url.replace("postgresql+psycopg2://", "postgresql://")
    else:
        pg_url = db_url

    parsed = up.urlparse(pg_url)
    user = parsed.username or "postgres"
    password = parsed.password or ""
    host = parsed.hostname or "localhost"
    port = parsed.port or 5432
    dbname = parsed.path.lstrip("/") or "remote_workforce"

    # Connect to default 'postgres' database to create target DB if missing
    try:
        conn = psycopg2.connect(dbname="postgres", user=user, password=password, host=host, port=port)
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    except Exception as e:
        print(f"Failed to connect to server to create database: {e}")
        sys.exit(1)

    try:
        cur = conn.cursor()
        cur.execute("SELECT 1 FROM pg_database WHERE datname = %s", (dbname,))
        exists = cur.fetchone() is not None
        if not exists:
            cur.execute(f"CREATE DATABASE \"{dbname}\"")
            print(f"Created database '{dbname}'.")
        else:
            print(f"Database '{dbname}' already exists.")
        cur.close()
    finally:
        conn.close()


if __name__ == "__main__":
    ensure_database_exists()
    # After DB exists, create tables via SQLAlchemy
    from db.database import init_db  # import after DB creation
    init_db()
    print("Initialized database schema.")
