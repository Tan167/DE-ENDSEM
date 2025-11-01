from __future__ import annotations
from typing import Optional
from werkzeug.security import generate_password_hash, check_password_hash


def hash_password(password: str) -> str:
    return generate_password_hash(password)


def verify_password(password: str, password_hash: Optional[str]) -> bool:
    if not password_hash:
        return False
    try:
        return check_password_hash(password_hash, password)
    except Exception:
        return False
