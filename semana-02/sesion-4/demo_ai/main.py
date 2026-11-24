import os
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from openai import OpenAI
from pydantic import BaseModel, Field

# Docker Compose + Model Runner inyectan estas vars vía `models:` en dockercompose.yaml.
LOG_PATH = Path(os.environ.get("LOG_PATH", "/data/app.log"))
STATIC_DIR = Path(__file__).resolve().parent / "static"

app = FastAPI(title="Estud-IA Bot")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class AskRequest(BaseModel):
    mensaje: str = Field(..., min_length=1, max_length=4000)


def modelo_config() -> tuple[str, str]:
    model_url = os.environ.get("MODEL_URL", "").strip()
    model_name = os.environ.get("MODEL_NAME", "").strip()
    if not model_url or not model_name:
        raise HTTPException(
            status_code=503,
            detail=(
                "Faltan MODEL_URL / MODEL_NAME. Arranca el stack con "
                "`docker compose -f dockercompose.yaml up --build` para que "
                "Docker Model Runner inyecte el endpoint del modelo."
            ),
        )
    return model_url, model_name


def cliente_modelo() -> tuple[OpenAI, str]:
    model_url, model_name = modelo_config()
    return OpenAI(base_url=model_url, api_key="no-key"), model_name


def leer_log(n: int = 20) -> str:
    if not LOG_PATH.exists():
        return "(no hay log disponible)"
    lines = LOG_PATH.read_text(encoding="utf-8", errors="replace").splitlines()
    return "\n".join(lines[-n:])


def preguntar_modelo(mensaje_usuario: str) -> str:
    client, model_name = cliente_modelo()
    log = leer_log()
    try:
        r = client.chat.completions.create(
            model=model_name,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Eres Estud-IA Bot, un asistente de operaciones cloud. "
                        "Responde en español y breve. Usa el log cuando ayude; "
                        "si falta información, dilo."
                    ),
                },
                {
                    "role": "user",
                    "content": f"Log reciente:\n{log}\n\nPregunta del usuario:\n{mensaje_usuario}",
                },
            ],
        )
    except Exception as exc:
        raise HTTPException(
            status_code=502,
            detail=f"Error al llamar al Docker Model Runner ({model_name}): {exc}",
        ) from exc

    content = r.choices[0].message.content
    if not content:
        raise HTTPException(status_code=502, detail="El modelo no devolvió contenido")
    return content


@app.get("/health")
def health():
    model_url = os.environ.get("MODEL_URL", "")
    model_name = os.environ.get("MODEL_NAME", "")
    return {
        "ok": True,
        "docker_model_runner": bool(model_url and model_name),
        "model": model_name or None,
        "model_url_set": bool(model_url),
    }


@app.post("/ask")
def ask(body: AskRequest):
    return {"respuesta": preguntar_modelo(body.mensaje.strip())}


@app.post("/diagnosticar")
def diagnosticar():
    return {
        "respuesta": preguntar_modelo(
            "¿Qué falla ves en el log y qué comprobarías primero?"
        )
    }


@app.get("/")
def index():
    return FileResponse(STATIC_DIR / "index.html")
