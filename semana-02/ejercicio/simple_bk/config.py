import os

from dotenv import load_dotenv

load_dotenv()

# Sin str(): si la variable no existe, getenv devuelve None y la validación sí falla.
CRIPTO_SECRET_KEY = os.getenv("SECRET_KEY")
APP_ENV = os.getenv("APP_ENV", "development")
PORT = os.getenv("PORT", "8000")


if not CRIPTO_SECRET_KEY:
    raise ValueError(
        "Falta SECRET_KEY. Defínela en el entorno o en el archivo .env "
        "(puedes partir de .env.example; usa un valor ficticio)."
    )
