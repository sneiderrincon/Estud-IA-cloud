## Reto: la imagen más ligera

**Objetivo.** Construir la imagen más pequeña que puedas para este proyecto, sin que deje de funcionar.

**Punto de partida.** Usa como base el archivo `Dockerfile.inicial`. Construye primero esa imagen tal cual y anota su peso: será tu referencia ("antes").

### Reglas

1. Tu imagen debe **seguir haciendo lo mismo** que la inicial: arrancar y responder a la operación de prueba del servicio. Una imagen pequeña que no funciona no cuenta.
2. Puedes cambiar el Dockerfile y los archivos de construcción que necesites (por ejemplo, `.dockerignore`). No puedes quitar funcionalidad del servicio.
3. No incluyas secretos ni credenciales en la imagen.
4. Puedes usar herramientas de IA, pero debes poder explicar cada cambio que dejaste y por qué reduce el peso.

### Cómo medir

Construye con una etiqueta que identifique cada intento y compara los pesos:

```bash
docker build -f Dockerfile.inicial -t reto:inicial .
docker build -t reto:mejorada .
docker image ls reto
```

Anota también cuánto tardó cada build.

### Qué entregar al chat del curso

1. El pantallazo de la salida de `docker image ls reto`, donde se vean **las dos imágenes** (inicial y mejorada) con su tamaño.
2. Una captura o línea de salida que muestre que tu imagen mejorada **arranca y responde** (por ejemplo, el resultado de la operación de prueba).
3. Una frase respondiendo: **¿cuál fue el cambio que más peso te quitó?**

### Pistas (sin dar la respuesta)

- Mira qué hay dentro de la imagen y pregúntate cuánto de eso se necesita para **ejecutar** el servicio, no para construirlo.
- El orden de las instrucciones del Dockerfile y lo que copias al contexto de construcción importan.
- Antes de cambiar nada, `docker history reto:inicial` te muestra qué capas pesan más.

### Cómo se compara

Gana quien logre menos MiB con la imagen funcionando. En empate, se prefiere el Dockerfile más fácil de leer y de mantener.