from typing import Any
from app.core.database import get_database


def get_db() -> Any:
    return get_database()
