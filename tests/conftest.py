import os
import sys
import pytest


# Ensure project root is on sys.path for `import app`
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)


@pytest.fixture(autouse=True)
def _disable_auth_defaults():
    # Por defecto, deshabilitar auth en tests, salvo que el test lo configure.
    from app.core.config import settings
    settings.API_KEYS = ""
    settings.JWT_SECRET = None
    yield


@pytest.fixture(scope="session")
def anyio_backend():
    # Fuerza backend asyncio para evitar cierres de loop con TestClient
    return "asyncio"
