FROM python:3.12-slim

WORKDIR /app

COPY app/ ./app/

# Vulnerabilidad: incorporamos credenciales a una layer
COPY .env /app/.env

# Falsa solución: borrar el archivo en una layer posterior
RUN rm /app/.env

EXPOSE 8000

CMD ["python", "app/main.py"]