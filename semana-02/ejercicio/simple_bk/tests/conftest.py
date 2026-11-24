import os
import sys
from pathlib import Path

import pytest
from cryptography.fernet import Fernet
from fastapi.testclient import TestClient

RAIZ = Path(__file__).resolve().parents[1]
if str(RAIZ) not in sys.path:
    sys.path.insert(0, str(RAIZ))

# Clave ficticia generada en la sesión. No se versiona y no es un secreto real.
os.environ["SECRET_KEY"] = Fernet.generate_key().decode()

from main import app  # noqa: E402


@pytest.fixture
def cliente():
    with TestClient(app) as cliente_http:
        yield cliente_http
