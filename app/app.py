from __future__ import annotations
"""Legacy entrypoint wrapper.
Prefer running Home.py. This module forwards to Home so imports remain consistent.
"""
import os, sys

# Ensure the app directory is importable for top-level modules (config, db, utils)
APP_DIR = os.path.dirname(__file__)
if APP_DIR not in sys.path:
    sys.path.insert(0, APP_DIR)

# Forward import to Home which sets up the Streamlit page
from Home import *  # noqa: F401,F403

if __name__ == "__main__":
    # Home module has its own __main__ logic; nothing to do here.
    pass
