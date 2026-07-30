# Informe de rutas — ABM AI Service

Todas las rutas requieren el header `X-API-Key` (dependencia global del router). Todas responden con el envoltorio estándar `APIResponse`: `{ success, message, data, error }`.

---

## DELETE

**1- ruta:** `/delete/embedding/{embedding_id}`

**propósito:** elimina un único embedding (imagen) puntual, sin afectar al resto de las imágenes del mismo vehículo.

**espera:** `embedding_id` (path param, string)

**retorna:**
```json
{
    "success": true,
    "message": "Embedding {embedding_id} eliminado correctamente",
    "data": {
        "vehicle_id": "<uuid>",
        "embedding_id": "<embedding_id>"
    },
    "error": null
}
```
Si `embedding_id` no existe → `404 NOT_FOUND`.

---

**2- ruta:** `/delete/{vehicle_id}`

**propósito:** elimina todos los embeddings asociados a un vehículo.

**espera:** `vehicle_id` (path param, UUID)

**retorna:**
```json
{
    "success": true,
    "message": "Se eliminaron las imagenes asociadas a la entidad con UUID {vehicle_id}",
    "data": { "...": "resultado crudo de la operación de borrado en Qdrant (status, etc.)" },
    "error": null
}
```
No valida si realmente había puntos con ese `vehicle_id`: si no existía ninguno, igual responde éxito (borrado de 0 puntos).

---

## PATCH

**1- ruta:** `/update-label`

**propósito:** actualiza la etiqueta (`label`, el sector fotografiado) de una imagen puntual.

**espera:** body JSON
```json
{
    "embedding_id": "<embedding_id>",
    "new_label": "<nueva etiqueta>"
}
```

**retorna:**
```json
{
    "success": true,
    "message": "Etiqueta actualizada correctamente para el vector {embedding_id}",
    "data": {
        "vehicle_id": "<uuid>",
        "embedding_id": "<embedding_id>",
        "label": "<nueva etiqueta>",
        "license_plate": "<patente o null>"
    },
    "error": null
}
```
Si `embedding_id` no existe → `404 NOT_FOUND`. Si `new_label` viene vacío → `400 BAD_REQUEST`.

---

**2- ruta:** `/images/{embedding_id}`

**propósito:** reemplaza la imagen (y por lo tanto el embedding) de un punto ya indexado, conservando el resto de sus metadatos (vehicle_id, label, brand, model, color, license_plate, details).

**espera:** `embedding_id` (path param) + `file` (multipart, la nueva imagen)

**retorna:**
```json
{
    "success": true,
    "message": "Imagen reemplazada correctamente para el vector {embedding_id}",
    "data": {
        "vehicle_id": "<uuid>",
        "embedding_id": "<embedding_id>",
        "label": "<label existente, sin cambios>",
        "license_plate": "<patente existente, sin cambios>"
    },
    "error": null
}
```
Si `embedding_id` no existe → `404 NOT_FOUND`. No vuelve a correr ANPR sobre la nueva imagen (la patente del vehículo no se recalcula acá).

---

**3- ruta:** `/vehicles/{vehicle_id}`

**propósito:** actualiza parcialmente los metadatos compartidos de un vehículo (`brand`, `model`, `color`, `license_plate`) en **todas** sus imágenes indexadas, en una sola operación. `details` NO se edita acá (es un atributo por imagen, se corrige reemplazando esa imagen puntual).

**espera:** `vehicle_id` (path param) + body JSON con cualquier subconjunto de:
```json
{
    "brand": "Toyota",
    "model": "Corolla",
    "color": "Gris",
    "license_plate": "AA021ID"
}
```

**retorna:**
```json
{
    "success": true,
    "message": "Metadatos actualizados en {N} imagen(es) del vehículo {vehicle_id}",
    "data": {
        "vehicle_id": "<uuid>",
        "updated_images": 3,
        "updated_fields": { "...": "solo los campos enviados" }
    },
    "error": null
}
```
Si no se envía ningún campo → `400 BAD_REQUEST`. Si `vehicle_id` no existe → `404 NOT_FOUND`.

---

## POST

**1- ruta:** `/ingest`

**propósito:** sube e indexa un lote de imágenes de un vehículo. La patente se recibe manualmente dentro de `metadata` — el reconocimiento automático (ANPR) NO se usa en la ingesta, es exclusivo de `/search/image`. Cada imagen tiene UN solo label (el sector) pero puede tener VARIOS `details` (ej. abolladura y vidrio roto en la misma foto).

**espera:** form-data
```
metadata: str              (JSON, ver formato abajo)
files: List[UploadFile]    (en el MISMO ORDEN que metadata.images)
```
Formato de `metadata`:
```json
{
    "vehicle_id": "8308f88e-55ac-46a0-8d41-7988f2d85248",
    "brand": "Toyota",
    "model": "Corolla",
    "color": "Blanco",
    "license_plate": "AA021ID",
    "images": [
        { "label": "frente", "details": [] },
        { "label": "atras", "details": ["abolladura", "vidrio roto"] }
    ]
}
```

**retorna:**
```json
{
    "success": true,
    "message": "Imágenes indexadas correctamente para el vehiculo con id {vehicle_id}",
    "data": [
        {
            "vehicle_id": "<uuid>",
            "embedding_id": "<uuid generado>",
            "label": "frente",
            "license_plate": "AA021ID",
            "details": []
        },
        {
            "vehicle_id": "<uuid>",
            "embedding_id": "<uuid generado>",
            "label": "atras",
            "license_plate": "AA021ID",
            "details": ["abolladura", "vidrio roto"]
        }
    ],
    "error": null
}
```
Si falla una imagen a mitad del lote, revierte (rollback) las que ya se habían insertado.

---

**2- ruta:** `/search/image`

**propósito:** busca vehículos similares a partir de una imagen. Primero intenta identificar una patente (ANPR); si la encuentra con confianza suficiente, busca por match exacto de patente. Si no, usa similitud visual (embedding CLIP) con umbral dinámico.

**espera:** `file` (multipart, la imagen a buscar)

**retorna:**
```json
{
    "success": true,
    "message": "Busqueda de imagen completada",
    "data": {
        "matches": [
            {
                "vehicle_id": "<uuid>",
                "images": [ { "score": 0.87, "label": "frente", "details": ["rayón puerta izquierda"] } ],
                "license_plate": "AA021ID",
                "brand": "Toyota",
                "model": "Corolla",
                "color": "Blanco"
            }
        ],
        "threshold": 0.5638777
    },
    "error": null
}
```
Si el match fue por patente exacta, `message` cambia a `"Vehículo encontrado por patente {patente}"` y `threshold` viene `null`.

---

**3- ruta:** `/search/text`

**propósito:** búsqueda semántica híbrida por texto en lenguaje natural (ej: "vehiculo marca toyota modelo corolla color blanco con rayon en puerta izquierda"). Combina: (1) similitud visual-semántica vía embedding CLIP del texto traducido al inglés (`deep_translator`), sin piso de score duro, y (2) un boost aditivo de puntaje por cada palabra clave del texto original en español que aparece en `brand/model/color/label/details` de cada imagen individual (el boost se calcula por imagen antes de agrupar, para que "izquierda" priorice la imagen de ese sector puntual, no todo el vehículo por igual).

**espera:** `text` (form, string)

**retorna:** mismo formato que `/search/image` (`SearchResponse`), con `message`: `"Busqueda para '{text}' realizada con éxito"`.

---

## Resumen

| Método | Ruta | Propósito |
|---|---|---|
| DELETE | `/delete/embedding/{embedding_id}` | Elimina 1 imagen puntual |
| DELETE | `/delete/{vehicle_id}` | Elimina todas las imágenes de un vehículo |
| PATCH | `/update-label` | Actualiza el label (sector) de 1 imagen |
| PATCH | `/images/{embedding_id}` | Reemplaza la imagen/embedding de 1 punto |
| PATCH | `/vehicles/{vehicle_id}` | Actualiza brand/model/color/license_plate de todo el vehículo |
| POST | `/ingest` | Sube e indexa un lote de imágenes de un vehículo (patente manual) |
| POST | `/search/image` | Busca por imagen (con ANPR-first) |
| POST | `/search/text` | Busca por texto en lenguaje natural (híbrida) |