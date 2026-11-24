import importlib.util
import os
import subprocess
import sys

import dotenv
import pytest
from cryptography.fernet import InvalidToken

from codes import decrypt, encrypt
from config import CRIPTO_SECRET_KEY
from conftest import RAIZ


def test_raiz_devuelve_el_mensaje(cliente):
    respuesta = cliente.get("/")
    assert respuesta.status_code == 200
    assert respuesta.json() == {"message": "Hello, this is a secret message!"}


def test_secret_con_message_hola(cliente):
    respuesta = cliente.get("/secret?message=hola")
    assert respuesta.status_code == 200
    cuerpo = respuesta.json()
    assert cuerpo["decrypted"] == "hola"
    assert isinstance(cuerpo["encrypted"], str)
    assert cuerpo["encrypted"].startswith("gAAAA")
    assert decrypt(cuerpo["encrypted"], CRIPTO_SECRET_KEY) == "hola"


def test_secret_sin_mensaje_responde_422(cliente):
    respuesta = cliente.get("/secret")
    assert respuesta.status_code == 422


def test_decrypt_usa_la_clave_que_recibe():
    cifrado = encrypt("hola")
    assert decrypt(cifrado, CRIPTO_SECRET_KEY) == "hola"
    with pytest.raises(InvalidToken):
        decrypt(cifrado, "clave-ficticia-distinta")


def test_docs_redoc_y_openapi(cliente):
    assert cliente.get("/docs").status_code == 200
    assert cliente.get("/redoc").status_code == 200
    esquema = cliente.get("/openapi.json")
    assert esquema.status_code == 200
    rutas = esquema.json()["paths"]
    assert "/" in rutas
    assert "/secret" in rutas


@pytest.mark.parametrize("modo", ["ausente", "vacia"])
def test_config_falla_en_este_proceso(modo, monkeypatch):
    # El mismo archivo, otro módulo: coverage ve el raise y no pisa config ya importado.
    monkeypatch.setattr(dotenv, "load_dotenv", lambda *args, **kwargs: False)
    if modo == "ausente":
        monkeypatch.delenv("SECRET_KEY", raising=False)
    else:
        monkeypatch.setenv("SECRET_KEY", "")
    spec = importlib.util.spec_from_file_location(
        f"config_sin_clave_{modo}",
        RAIZ / "config.py",
    )
    modulo = importlib.util.module_from_spec(spec)
    with pytest.raises(ValueError, match="SECRET_KEY"):
        spec.loader.exec_module(modulo)


@pytest.mark.parametrize("modo", ["ausente", "vacia"])
def test_falla_si_falta_secret_key(modo):
    # Proceso nuevo: config.py valida al importar y el padre ya tiene clave.
    script = """
import os
import dotenv

dotenv.load_dotenv = lambda *args, **kwargs: False
if os.environ["MODO_PRUEBA"] == "ausente":
    os.environ.pop("SECRET_KEY", None)
else:
    os.environ["SECRET_KEY"] = ""

try:
    import config
except ValueError as exc:
    texto = str(exc)
    if "SECRET_KEY" not in texto:
        raise SystemExit("el error no menciona SECRET_KEY: " + texto)
    print(texto)
    raise SystemExit(0)
raise SystemExit("config se importó sin una SECRET_KEY válida")
"""
    entorno = os.environ.copy()
    entorno["PYTHONPATH"] = str(RAIZ)
    entorno["MODO_PRUEBA"] = modo
    resultado = subprocess.run(
        [sys.executable, "-c", script],
        cwd=RAIZ,
        env=entorno,
        capture_output=True,
        text=True,
        check=False,
    )
    assert resultado.returncode == 0, resultado.stderr + resultado.stdout
    assert "SECRET_KEY" in resultado.stdout
