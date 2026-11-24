# simple_bk

API mínima con dos rutas: `/` responde un saludo y `/secret` cifra un mensaje con Fernet y lo devuelve también descifrado.

La clave no va en el código. Se lee de la variable `SECRET_KEY`. El valor de ejemplo es ficticio: no uses una clave de un servicio real.

## Requisitos

- Python 3.12
- [uv](https://docs.astral.sh/uv/)
- [just](https://just.systems/)
- Docker, solo si vas a construir la imagen

## Configuración

Desde esta carpeta:

```bash
cp .env.example .env
```

`.env` no se versiona. Puedes cambiar `SECRET_KEY` por otra cadena ficticia.

## Comandos

```bash
just install
just test
just run
```

`just test` también escribe `coverage.xml` en esta carpeta. Ese archivo no se versiona.

`just run` publica la API en `0.0.0.0` y en el puerto `PORT` (8000 si no lo defines). Con el servidor en marcha:

```bash
curl 'http://127.0.0.1:8000/secret?message=hola'
```

La respuesta trae `encrypted` (token Fernet) y `decrypted` (el mismo texto que enviaste).

## Docker

```bash
just docker-build
just docker-run
```

`docker-run` inyecta la misma clave ficticia de `.env.example`. La imagen no copia un `.env`.

## Dependencias

`fastapi` y `uvicorn` están en las dependencias de ejecución. `pytest` y `httpx` están en el grupo `dev`, porque solo hacen falta para los tests. `uv sync --no-dev` deja fuera ese grupo.
