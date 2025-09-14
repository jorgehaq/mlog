import time
from dataclasses import dataclass
from typing import Dict

from app.core.config import settings


@dataclass
class CircuitState:
    fails: int = 0
    opened_at: float | None = None


_circuits: Dict[str, CircuitState] = {}


def _state(key: str) -> CircuitState:
    if key not in _circuits:
        _circuits[key] = CircuitState()
    return _circuits[key]


def is_open(key: str) -> bool:
    if not settings.CIRCUIT_BREAKER_ENABLED:
        return False
    s = _state(key)
    if s.opened_at is None:
        return False
    # auto-recover after cooldown
    if (time.time() - s.opened_at) >= settings.CIRCUIT_BREAKER_RECOVERY_SECONDS:
        s.fails = 0
        s.opened_at = None
        return False
    return True


def record_success(key: str) -> None:
    s = _state(key)
    s.fails = 0
    s.opened_at = None


def record_failure(key: str) -> None:
    s = _state(key)
    s.fails += 1
    if settings.CIRCUIT_BREAKER_ENABLED and s.fails >= settings.CIRCUIT_BREAKER_FAILURES:
        s.opened_at = time.time()

