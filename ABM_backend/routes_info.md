# Informe de rutas — Vehicle Management API

Todas las rutas requieren el header `X-API-Key` (dependencia global del router, aplicada a nivel de `prefix="/vehicles"`). Todas responden con el envoltorio estándar de respuesta: `{ success, message, data, error }`.

Internamente, algunas rutas disparan además una llamada al **servicio de reconocimiento** (puerto 8001). Esa integración se indica en cada endpoint como **"Integración"**, junto con su modo: **estricto** (si falla, se cancela toda la operación) o **best effort** (si falla, se loguea pero la operación local no se revierte).

---

## GET

**1- ruta:** `/vehicles`

**propósito:** obtiene todos los vehículos registrados, junto con sus imágenes y detalles.

**espera:** sin parámetros.

**retorna:**
```json
{
    "success": true,
    "message": "Vehículos obtenidos correctamente.",
    "data": [
        {
            "id": "<uuid>",
            "license_plate": "AA123BB",
            "brand": "Toyota",
            "model": "Corolla",
            "color": "Blanco",
            "year": 2020,
            "insurance_policy": "POL-000123",
            "observations": "...",
            "is_active": true,
            "created_at": "...",
            "updated_at": "...",
            "images": [
                {
                    "id": "<uuid>",
                    "filename": "abc123.jpg",
                    "image_url": "https://storage.googleapis.com/...",
                    "label": "FRENTE",
                    "embedding_status": "COMPLETADO",
                    "details": [
                        { "id": "<uuid>", "detail_type": "RAYON", "description": "..." }
                    ]
                }
            ]
        }
    ],
    "error": null
}
```

---

**2- ruta:** `/vehicles/{vehicle_id}`

**propósito:** obtiene un vehículo puntual por su id.

**espera:** `vehicle_id` (path param, UUID)

**retorna:** mismo formato que un elemento individual de `GET /vehicles`.

Si `vehicle_id` no existe → `404 NOT_FOUND`.

---

## POST

**1- ruta:** `/vehicles`

**propósito:** crea un vehículo junto con sus imágenes y detalles. Cada imagen tiene un único `label` (sector) pero puede tener varios `details` (relación 1 a N).

**espera:** form-data
```
request: str               (JSON, ver formato abajo)
files: List[UploadFile]     (nombres deben coincidir con request.images[].filename)
```
Formato de `request`:
```json
{
    "license_plate": "AA123BB",
    "brand": "Toyota",
    "model": "Corolla",
    "color": "Blanco",
    "year": 2020,
    "insurance_policy": "POL-000123",
    "observations": "Vehiculo de prueba",
    "images": [
        {
            "filename": "frente.jpg",
            "label": "FRENTE",
            "details": [
                { "detail_type": "RAYON", "description": "Rayón leve en el paragolpes" }
            ]
        },
        {
            "filename": "atras.jpg",
            "label": "ATRAS",
            "details": []
        }
    ]
}
```

**retorna:**
```json
{
    "success": true,
    "message": "Vehículo creado correctamente.",
    "data": { "...": "VehicleResponse completo, ver GET /vehicles/{id}" },
    "error": null
}
```
Si la patente ya existe → `409 CONFLICT`. Si `images` está vacío → `400 BAD_REQUEST`. Si los archivos enviados no coinciden con los `filename` de `images` → `400 BAD_REQUEST`.

**Integración — best effort:** tras persistir el vehículo, se envían las imágenes al servicio de reconocimiento (`POST /ingest`), con cada imagen llevando su propio `label` y `details`. Si la indexación falla (total o parcialmente), la creación del vehículo **no se revierte**: las imágenes que no pudieron indexarse quedan con `embedding_status=PENDIENTE` para ser reintentadas más adelante. Las que sí se indexan quedan con `embedding_status=COMPLETADO`, `embedding_id` y `indexed_at` seteados.

---

**2- ruta:** `/vehicles/search/image`

**propósito:** busca vehículos visualmente similares a partir de una imagen.

**espera:** `file` (multipart, la imagen a buscar)

**retorna:**
```json
{
    "success": true,
    "message": "Búsqueda por imagen completada.",
    "data": {
        "threshold": 0.5638777,
        "matches": [
            {
                "vehicle": { "...": "VehicleResponse completo" },
                "score": 0.87,
                "matched_images": [
                    { "label": "frente", "score": 0.87, "details": ["rayón puerta izquierda"] }
                ]
            }
        ]
    },
    "error": null
}
```
Si el `vehicle_id` devuelto por el servicio de reconocimiento no existe en la base local (fue borrado), ese match se descarta silenciosamente (se loguea como warning).

**Integración:** delega la búsqueda vectorial en `POST /search/image` del servicio de reconocimiento. Si esa llamada falla → `500 INTERNAL_SERVER_ERROR`.

---

**3- ruta:** `/vehicles/search/text`

**propósito:** búsqueda semántica híbrida por texto en lenguaje natural (ej: "vehiculo marca toyota modelo corolla color blanco con rayon en puerta izquierda").

**espera:** `text` (form, string)

**retorna:** mismo formato que `search/image` (`VehicleSearchResponse`), con `message`: `"Búsqueda por texto completada."`.

Si `text` viene vacío o solo espacios → `400 BAD_REQUEST`.

**Integración:** delega la búsqueda híbrida en `POST /search/text` del servicio de reconocimiento. Si esa llamada falla → `500 INTERNAL_SERVER_ERROR`.

---

## PUT

**1- ruta:** `/vehicles/{vehicle_id}`

**propósito:** actualiza parcialmente los datos de un vehículo (cualquier subconjunto de campos).

**espera:** `vehicle_id` (path param) + body JSON con cualquier subconjunto de:
```json
{
    "license_plate": "AA123BB",
    "brand": "Toyota",
    "model": "Corolla",
    "color": "Gris",
    "year": 2021,
    "insurance_policy": "POL-000456",
    "observations": "...",
    "is_active": true
}
```

**retorna:**
```json
{
    "success": true,
    "message": "Vehículo actualizado correctamente.",
    "data": { "...": "VehicleResponse completo con los campos ya actualizados" },
    "error": null
}
```
Si `vehicle_id` no existe → `404 NOT_FOUND`. Si no se envía ningún campo → `400 BAD_REQUEST`. Si `license_plate` ya pertenece a otro vehículo → `409 CONFLICT`.

**Integración — best effort:** si cambian `brand`, `model`, `color` o `license_plate`, esos campos se replican en el servicio de reconocimiento vía `PATCH /vehicles/{vehicle_id}`, actualizando la metadata de todas las imágenes indexadas de ese vehículo. Si la llamada falla, se loguea pero **la actualización local ya persistida no se revierte**. `year`, `insurance_policy`, `observations` e `is_active` son propios del backend y no se replican (el servicio de reconocimiento no los conoce).

---

## PATCH

**1- ruta:** `/vehicles/{vehicle_id}/images/{image_id}/label`

**propósito:** actualiza el sector (`label`) de una imagen puntual.

**espera:** `vehicle_id` + `image_id` (path params) + body JSON:
```json
{
    "label": "LATERAL_IZQUIERDA"
}
```

**retorna:**
```json
{
    "success": true,
    "message": "Label de la imagen actualizado correctamente.",
    "data": { "...": "VehicleResponse completo, con el label ya actualizado" },
    "error": null
}
```
Si la imagen no existe o no pertenece a `vehicle_id` → `404 NOT_FOUND`.

**Integración — best effort:** si la imagen tiene `embedding_id` (ya fue indexada), el nuevo label se traduce con `IMAGE_LABEL_TO_RECOGNITION_LABEL` y se replica vía `PATCH /update-label` del servicio de reconocimiento. Si la imagen no tiene `embedding_id` (nunca se indexó o quedó `PENDIENTE`), el cambio queda solo local. Si la llamada al servicio falla, se loguea pero el label local no se revierte.

---

**2- ruta:** `/vehicles/{vehicle_id}/images/{image_id}/file`

**propósito:** reemplaza el archivo de una imagen puntual, conservando su `label` y `details`.

**espera:** `vehicle_id` + `image_id` (path params) + `file` (multipart, la nueva imagen)

**retorna:**
```json
{
    "success": true,
    "message": "Imagen reemplazada correctamente.",
    "data": { "...": "VehicleResponse completo, con image_url/filename actualizados" },
    "error": null
}
```
Si la imagen no existe o no pertenece a `vehicle_id` → `404 NOT_FOUND`.

**Integración:**
- Subida del nuevo archivo a Google Cloud Storage → **bloqueante** (si falla, se corta antes de tocar la base).
- Borrado del archivo anterior en Cloud Storage → **best effort** (si falla, se loguea; el archivo nuevo ya quedó persistido).
- Reemplazo del embedding en el servicio de reconocimiento (`PATCH /images/{embedding_id}`) → **best effort**, y solo si la imagen tenía `embedding_id`. El servicio de reconocimiento no vuelve a correr ANPR sobre la imagen nueva.

---

## DELETE

**1- ruta:** `/vehicles/{vehicle_id}`

**propósito:** elimina un vehículo junto con todas sus imágenes.

**espera:** `vehicle_id` (path param, UUID)

**retorna:**
```json
{
    "success": true,
    "message": "Vehiculo eliminado correctamente.",
    "data": null,
    "error": null
}
```
Si `vehicle_id` no existe → `404 NOT_FOUND`.

**Integración — modo estricto (ambos pasos externos son bloqueantes, en este orden):**
1. `DELETE /delete/{vehicle_id}` en el servicio de reconocimiento (borra todos los vectores del vehículo). Si falla → `500 INTERNAL_SERVER_ERROR`, el vehículo **no se borra**.
2. Borrado de cada archivo de imagen en Google Cloud Storage. Si falla → `500 INTERNAL_SERVER_ERROR`, el vehículo **no se borra**.

Solo si ambos pasos externos se completan sin error, se borra el vehículo (y en cascada sus imágenes/detalles) de PostgreSQL.

---

**2- ruta:** `/vehicles/{vehicle_id}/images/{image_id}`

**propósito:** elimina una única imagen puntual, sin afectar al resto de las imágenes del vehículo.

**espera:** `vehicle_id` + `image_id` (path params, UUID)

**retorna:**
```json
{
    "success": true,
    "message": "Imagen eliminada correctamente.",
    "data": null,
    "error": null
}
```
Si la imagen no existe o no pertenece a `vehicle_id` → `404 NOT_FOUND`.

**Integración — modo estricto (mismo criterio que el borrado de vehículo completo):**
1. Si la imagen tiene `embedding_id`: `DELETE /delete/embedding/{embedding_id}` en el servicio de reconocimiento. Si falla → `500 INTERNAL_SERVER_ERROR`, la imagen **no se borra**. Si la imagen no tiene `embedding_id`, este paso se omite.
2. Borrado del archivo en Google Cloud Storage. Si falla → `500 INTERNAL_SERVER_ERROR`, la imagen **no se borra**.

Solo si ambos pasos se completan sin error, se borra la imagen (y en cascada sus detalles) de PostgreSQL.

---

## Resumen

| Método | Ruta | Propósito | Integración con servicio de reconocimiento |
|---|---|---|---|
| GET | `/vehicles` | Lista todos los vehículos | — |
| GET | `/vehicles/{vehicle_id}` | Obtiene un vehículo | — |
| POST | `/vehicles` | Crea un vehículo con imágenes | `POST /ingest` (best effort) |
| POST | `/vehicles/search/image` | Busca por imagen | `POST /search/image` |
| POST | `/vehicles/search/text` | Busca por texto | `POST /search/text` |
| PUT | `/vehicles/{vehicle_id}` | Actualiza datos del vehículo | `PATCH /vehicles/{vehicle_id}` (best effort) |
| PATCH | `/vehicles/{vehicle_id}/images/{image_id}/label` | Actualiza el label de 1 imagen | `PATCH /update-label` (best effort) |
| PATCH | `/vehicles/{vehicle_id}/images/{image_id}/file` | Reemplaza el archivo de 1 imagen | `PATCH /images/{embedding_id}` (best effort) |
| DELETE | `/vehicles/{vehicle_id}` | Elimina un vehículo completo | `DELETE /delete/{vehicle_id}` (estricto) |
| DELETE | `/vehicles/{vehicle_id}/images/{image_id}` | Elimina 1 imagen puntual | `DELETE /delete/embedding/{embedding_id}` (estricto, si existe) |

---

## Nota sobre inconsistencia entre GET y DELETE de imagen

Los endpoints de imagen (`update-label`, reemplazo de archivo, eliminación) usan `vehicle_id` + `image_id` en el path como sub-recurso de vehículo, ya que así está organizado el resto del router de `/vehicles`. Esto difiere del servicio de reconocimiento, que identifica las imágenes por `embedding_id` de forma plana (`/update-label`, `/images/{embedding_id}`, `/delete/embedding/{embedding_id}`). La traducción entre ambos identificadores (`image_id` local ↔ `embedding_id` remoto) la resuelve `VehicleService` internamente antes de llamar al servicio de reconocimiento.