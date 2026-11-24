# demo_ai — Estud-IA Bot + Docker Model Runner

El punto de esta demo es **probar un modelo servido por Docker Model Runner** desde una API FastAPI (y una UI mínima).

Compose declara el modelo `ai/smollm2`, Model Runner lo descarga/sirve, e inyecta en el contenedor:

- `MODEL_URL` — endpoint OpenAI-compatible del runner
- `MODEL_NAME` — id del modelo

## Requisitos

- Docker Desktop con **Docker Model Runner** activado
- Docker Compose **≥ 2.38**

## Arranque

```bash
docker compose -f dockercompose.yaml up --build
```

Abre [http://localhost:8000](http://localhost:8000) (Estud-IA Bot).

Comprueba que el modelo quedó inyectado:

```bash
curl -s http://localhost:8000/health
# "docker_model_runner": true, "model": "ai/smollm2"
```

## Endpoints

| Método | Ruta | Uso |
|--------|------|-----|
| `GET` | `/` | UI Estud-IA Bot |
| `GET` | `/health` | Estado + si DMR inyectó el modelo |
| `POST` | `/ask` | `{"mensaje":"..."}` → respuesta del modelo |
| `POST` | `/diagnosticar` | Pregunta fija sobre `/data/app.log` |
