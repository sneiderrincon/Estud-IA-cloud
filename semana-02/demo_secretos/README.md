# Laboratorio de Seguridad Docker: Recuperación de secretos desde las capas de una imagen

## Objetivo

Comprender cómo la información sensible puede permanecer dentro de una imagen Docker, incluso después de que un archivo haya sido eliminado en una capa posterior del proceso de construcción.

En este laboratorio construiremos intencionalmente una imagen Docker vulnerable utilizando Docker Compose, inspeccionaremos sus capas y recuperaremos credenciales de un archivo que ya no existe dentro del contenedor en ejecución.

> **Advertencia:** Este laboratorio utiliza credenciales ficticias. Nunca utilices credenciales reales ni publiques esta imagen en un registry público.

---

## 1. Requisitos

Necesitas tener instalado:

- Docker
- Docker Compose
- `tar`
- `jq`

Verifica tu entorno:

```bash
docker --version
docker compose version
jq --version
```

---

## 2. Descarga o clona el laboratorio

Abre una terminal dentro del directorio del proyecto:

```bash
cd demo_secretos
```

---

## 3. Crear el archivo de variables de entorno

Crea el archivo `.env` a partir del ejemplo:

```bash
cp .env.example .env
```

Revisa las credenciales:

```bash
cat .env
```

El archivo contiene credenciales ficticias de AWS, una cadena de conexión a una base de datos y un token de API.

---

## 4. Construir la imagen vulnerable

Construye la imagen utilizando Docker Compose:

```bash
docker compose build
```

Durante la construcción, Docker ejecutará las siguientes operaciones:

1. Copia la aplicación.
2. Copia el archivo `.env` dentro de la imagen.
3. Elimina `.env` en una capa posterior.

El desarrollador cree que las credenciales ya no están presentes en la imagen final.

---

## 5. Iniciar la aplicación

```bash
docker compose up -d
```

Verifica que el contenedor esté ejecutándose:

```bash
docker compose ps
```

Prueba la aplicación:

```bash
curl http://localhost:8000
```

Respuesta esperada:

```text
Docker Security Demo - Running
```

---

## 6. Verificar que el secreto no está en el filesystem final

Ejecuta:

```bash
docker compose exec app ls -la /app
```

Comprueba que `.env` no aparece en el listado.

Intenta leerlo:

```bash
docker compose exec app cat /app/.env
```

Resultado esperado: el archivo no existe.

En este punto, el desarrollador cree que las credenciales están seguras.

---

## 7. Exportar la imagen Docker

Identifica la imagen:

```bash
docker images
```

La imagen que construimos se llama:

```text
docker-secrets-demo:insecure
```

Exporta la imagen:

```bash
docker save docker-secrets-demo:insecure -o image.tar
```

El archivo exportado contiene la configuración de la imagen, el manifest y las capas del filesystem.

---

## 8. Extraer la imagen exportada

Crea un directorio:

```bash
mkdir image-extracted
```

Extrae el archivo:

```bash
tar -xf image.tar -C image-extracted
```

Inspecciona su contenido:

```bash
ls -la image-extracted
```

Revisa el manifest:

```bash
cat image-extracted/manifest.json
```

El manifest permite identificar las capas del filesystem asociadas a la imagen.

---

## 9. Extraer cada capa de la imagen

Crea un directorio para las capas extraídas:

```bash
mkdir layers
```

Ejecuta:

```bash
jq -r '.[0].Layers[]' image-extracted/manifest.json | while read layer; do
    name=$(echo "$layer" | tr '/' '_')
    mkdir -p "layers/$name"
    tar -xf "image-extracted/$layer" -C "layers/$name"
done
```

Cada capa de la imagen ahora estará extraída en su propio directorio.

---

## 10. Buscar las credenciales expuestas

Busca las credenciales utilizadas en este laboratorio:

```bash
grep -RniE \
  "super-secret-demo|demo-password|demo-token|AKIADEMO" \
  layers/
```

Deberías poder encontrar el archivo `.env` original y recuperar sus valores.

También puedes buscar patrones comunes relacionados con credenciales:

```bash
grep -RniE \
  "SECRET|PASSWORD|TOKEN|API_KEY|AWS_SECRET|DATABASE_URL" \
  layers/
```

---

## 11. Investigar el historial de la imagen Docker

Inspecciona el historial de construcción de la imagen:

```bash
docker history --no-trunc docker-secrets-demo:insecure
```

Identifica qué instrucciones introdujeron el secreto y cuál fue la instrucción que eliminó el archivo.

Recuerda: el historial de la imagen es útil para entender el proceso de construcción, pero la inspección de las capas es lo que nos permite recuperar el contenido de los archivos.

---

## 12. Limpiar el entorno

Detén la aplicación:

```bash
docker compose down
```

Elimina la imagen:

```bash
docker image rm docker-secrets-demo:insecure
```

Elimina el archivo exportado y los directorios de extracción:

```bash
rm -rf image.tar image-extracted layers
```

---

## Preguntas

1. ¿Por qué `.env` no existe en el contenedor final, pero podemos recuperarlo desde la imagen?
2. ¿Cuál es la diferencia entre una capa Docker y el filesystem final del contenedor?
3. ¿Por qué ejecutar `RUN rm .env` no elimina de forma segura la capa anterior?
4. ¿Cuál es el propósito de `.dockerignore`?
5. ¿Por qué `ARG` y `ENV` no son mecanismos apropiados para almacenar secretos?
6. ¿Cómo proporcionarías de forma segura un secreto que se necesita durante la construcción de una imagen Docker?
7. ¿Cómo deberían entregarse los secretos a una aplicación que se ejecuta en producción?
8. Si una imagen que contiene un secreto real fue publicada en un registry, ¿es suficiente con eliminar la imagen? ¿Qué otras acciones deberían realizarse?

## Reto final

Modifica el Dockerfile y la configuración de Docker Compose para evitar que el secreto sea incorporado a la imagen.

Explica tu solución y demuestra que el secreto ya no puede recuperarse de las capas de la imagen.

