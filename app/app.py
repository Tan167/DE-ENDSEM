from __future__ import annotations
"""Legacy entrypoint wrapper.
Prefer running Home.py. This module forwards to Home so imports remain consistent.
"""
import os, sys

APP_DIR = os.path.dirname(__file__)
if APP_DIR not in sys.path:
    sys.path.insert(0, APP_DIR)

from Home import *  

if __name__ == "__main__":
    pass
