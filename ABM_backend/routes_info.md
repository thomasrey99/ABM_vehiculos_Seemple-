# Informe de rutas — Vehicle Management API

Todas las rutas requieren el header `X-API-Key` (dependencia global del router, aplicada a nivel de `prefix="/vehicles"`). Todas responden con el envoltorio estándar de respuesta: `{ success, message, data, error }`.

Internamente, algunas rutas disparan además una llamada al **servicio de reconocimiento** (puerto 8001) y/o a **OpenAI** (detección de daños / extracción de filtros). Esa integración se indica en cada endpoint como **"Integración"**, junto con su modo: **estricto** (si falla, se cancela toda la operación) o **best effort** (si falla, se loguea pero la operación local no se revierte).

Cada endpoint que devuelve un vehículo muestra el JSON completo, con todos sus campos (incluyendo imágenes y detalles), sin abreviar.

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
            "id": "8308f88e-55ac-46a0-8d41-7988f2d85248",
            "license_plate": "AA123BB",
            "brand": "Toyota",
            "model": "Corolla",
            "color": "Blanco",
            "year": 2020,
            "insurance_policy": "POL-000123",
            "observations": "Vehiculo de prueba",
            "is_active": true,
            "created_at": "2026-01-15T14:32:00Z",
            "updated_at": "2026-01-15T14:32:00Z",
            "images": [
                {
                    "id": "3f9c1e2a-1234-4a5b-9c3d-1234567890ab",
                    "filename": "abc123.jpg",
                    "image_url": "https://storage.googleapis.com/bucket/vehicles/8308f88e-55ac-46a0-8d41-7988f2d85248/abc123.jpg",
                    "label": "FRENTE",
                    "embedding_status": "COMPLETADO",
                    "details": [
                        {
                            "id": "7a1b2c3d-4e5f-6789-0abc-def123456789",
                            "detail_type": "RAYON",
                            "description": "Rayón leve en el paragolpes"
                        }
                    ]
                },
                {
                    "id": "9d8e7f6a-5b4c-3d2e-1f0a-987654321fed",
                    "filename": "def456.jpg",
                    "image_url": "https://storage.googleapis.com/bucket/vehicles/8308f88e-55ac-46a0-8d41-7988f2d85248/def456.jpg",
                    "label": "ATRAS",
                    "embedding_status": "PENDIENTE",
                    "details": []
                }
            ]
        }
    ],
    "error": null
}
```

`data` es un array con cero, uno o más objetos con esta misma estructura (uno por cada vehículo registrado). Campos de cada vehículo:

| Campo | Tipo | Descripción |
|---|---|---|
| `id` | UUID | Identificador del vehículo. |
| `license_plate` | string | Patente, normalizada a mayúsculas. |
| `brand` | string | Marca. |
| `model` | string | Modelo. |
| `color` | string \| null | Color. |
| `year` | integer \| null | Año de fabricación. |
| `insurance_policy` | string \| null | Número/identificador de póliza de seguro. |
| `observations` | string \| null | Observaciones libres. |
| `is_active` | boolean | Si el vehículo está activo en el sistema. |
| `created_at` | datetime | Fecha de creación. |
| `updated_at` | datetime | Fecha de última modificación. |
| `images` | array | Imágenes asociadas al vehículo. |
| `images[].id` | UUID | Identificador de la imagen. |
| `images[].filename` | string | Nombre del archivo tal como quedó guardado en Cloud Storage (no necesariamente el nombre original subido por el cliente). |
| `images[].image_url` | string | URL pública en Google Cloud Storage. |
| `images[].label` | string (enum `ImageLabel`) | Sector fotografiado: `FRENTE`, `ATRAS`, `LATERAL_IZQUIERDA`, `LATERAL_DERECHA`, `FRENTE_IZQUIERDA`, `FRENTE_DERECHA`, `ATRAS_IZQUIERDA`, `ATRAS_DERECHA`, `OTRO`. |
| `images[].embedding_status` | string (enum `EmbeddingStatus`) | Estado de indexación en el servicio de reconocimiento: `PENDIENTE`, `PROCESANDO`, `COMPLETADO`, `ERROR`. |
| `images[].details` | array | Daños detectados en esa imagen puntual. |
| `images[].details[].id` | UUID | Identificador del detalle. |
| `images[].details[].detail_type` | string (enum `ImageDetailType`) | Tipo de daño: `ABOLLADURA`, `VIDRIO_ROTO`, `RAYON`, `GRIETA`, `ROTO`, `OXIDO`, `CALCOMANIA`, `PIEZA_FALTANTE`, `DANO_PINTURA`, `DEFORMACION`, `CHOQUE`, `OTRO_COLOR`, `OTRO`. |
| `images[].details[].description` | string \| null | Descripción breve y libre del daño. |

---

**2- ruta:** `/vehicles/{vehicle_id}`

**propósito:** obtiene un vehículo puntual por su id.

**espera:** `vehicle_id` (path param, UUID).

**retorna:**
```json
{
    "success": true,
    "message": "Vehículo obtenido correctamente.",
    "data": {
        "id": "8308f88e-55ac-46a0-8d41-7988f2d85248",
        "license_plate": "AA123BB",
        "brand": "Toyota",
        "model": "Corolla",
        "color": "Blanco",
        "year": 2020,
        "insurance_policy": "POL-000123",
        "observations": "Vehiculo de prueba",
        "is_active": true,
        "created_at": "2026-01-15T14:32:00Z",
        "updated_at": "2026-01-15T14:32:00Z",
        "images": [
            {
                "id": "3f9c1e2a-1234-4a5b-9c3d-1234567890ab",
                "filename": "abc123.jpg",
                "image_url": "https://storage.googleapis.com/bucket/vehicles/8308f88e-55ac-46a0-8d41-7988f2d85248/abc123.jpg",
                "label": "FRENTE",
                "embedding_status": "COMPLETADO",
                "details": [
                    {
                        "id": "7a1b2c3d-4e5f-6789-0abc-def123456789",
                        "detail_type": "RAYON",
                        "description": "Rayón leve en el paragolpes"
                    }
                ]
            },
            {
                "id": "9d8e7f6a-5b4c-3d2e-1f0a-987654321fed",
                "filename": "def456.jpg",
                "image_url": "https://storage.googleapis.com/bucket/vehicles/8308f88e-55ac-46a0-8d41-7988f2d85248/def456.jpg",
                "label": "ATRAS",
                "embedding_status": "PENDIENTE",
                "details": []
            }
        ]
    },
    "error": null
}
```

El significado de cada campo es el mismo que el detallado en `GET /vehicles`.

Si `vehicle_id` no existe → `404 NOT_FOUND`.

---

**3- ruta:** `/vehicles/patente/{license_plate}`

**propósito:** obtiene un vehículo puntual por su patente.

**espera:** `license_plate` (path param, string). Se normaliza internamente a mayúsculas antes de buscar, por lo que no es sensible a mayúsculas/minúsculas.

**retorna:**
```json
{
    "success": true,
    "message": "Vehículo obtenido correctamente.",
    "data": {
        "id": "8308f88e-55ac-46a0-8d41-7988f2d85248",
        "license_plate": "AA123BB",
        "brand": "Toyota",
        "model": "Corolla",
        "color": "Blanco",
        "year": 2020,
        "insurance_policy": "POL-000123",
        "observations": "Vehiculo de prueba",
        "is_active": true,
        "created_at": "2026-01-15T14:32:00Z",
        "updated_at": "2026-01-15T14:32:00Z",
        "images": [
            {
                "id": "3f9c1e2a-1234-4a5b-9c3d-1234567890ab",
                "filename": "abc123.jpg",
                "image_url": "https://storage.googleapis.com/bucket/vehicles/8308f88e-55ac-46a0-8d41-7988f2d85248/abc123.jpg",
                "label": "FRENTE",
                "embedding_status": "COMPLETADO",
                "details": [
                    {
                        "id": "7a1b2c3d-4e5f-6789-0abc-def123456789",
                        "detail_type": "RAYON",
                        "description": "Rayón leve en el paragolpes"
                    }
                ]
            },
            {
                "id": "9d8e7f6a-5b4c-3d2e-1f0a-987654321fed",
                "filename": "def456.jpg",
                "image_url": "https://storage.googleapis.com/bucket/vehicles/8308f88e-55ac-46a0-8d41-7988f2d85248/def456.jpg",
                "label": "ATRAS",
                "embedding_status": "PENDIENTE",
                "details": []
            }
        ]
    },
    "error": null
}
```

El significado de cada campo es el mismo que el detallado en `GET /vehicles`.

Si no existe ningún vehículo con esa patente → `404 NOT_FOUND`.

---

## POST

**1- ruta:** `/vehicles`

**propósito:** crea un vehículo junto con sus imágenes y detalles. Cada imagen tiene un único `label` (sector) pero puede tener varios `details` (relación 1 a N).

**espera:** `multipart/form-data` con dos campos:

- `request` (string, JSON serializado): datos del vehículo y de sus imágenes.
- `files` (lista de archivos): los archivos de imagen en sí. El `filename` de cada archivo subido debe coincidir exactamente, uno a uno (como conjunto), con los `filename` declarados dentro de `request.images[]`.

Formato completo de `request`:
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
                {
                    "detail_type": "RAYON",
                    "description": "Rayón leve en el paragolpes"
                }
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

Campos de `request`:

| Campo | Tipo | Obligatorio | Descripción |
|---|---|---|---|
| `license_plate` | string (5 a 15 caracteres) | sí | Patente del vehículo. |
| `brand` | string (1 a 50 caracteres) | sí | Marca. |
| `model` | string (1 a 50 caracteres) | sí | Modelo. |
| `color` | string (máx. 50 caracteres) | no | Color. |
| `year` | integer (1900 a 2100) | no | Año de fabricación. |
| `insurance_policy` | string (máx. 50 caracteres) | no | Número/identificador de póliza de seguro. |
| `observations` | string (máx. 2000 caracteres) | no | Observaciones libres. |
| `images` | array (mínimo 1 elemento) | sí | Lista de imágenes a asociar. |

Cada elemento de `images`:

| Campo | Tipo | Obligatorio | Descripción |
|---|---|---|---|
| `filename` | string (1 a 255 caracteres) | sí | Nombre del archivo, debe coincidir con uno de los archivos enviados en `files`. |
| `label` | string (enum `ImageLabel`) | sí | Sector fotografiado. Valores válidos: `FRENTE`, `ATRAS`, `LATERAL_IZQUIERDA`, `LATERAL_DERECHA`, `FRENTE_IZQUIERDA`, `FRENTE_DERECHA`, `ATRAS_IZQUIERDA`, `ATRAS_DERECHA`, `OTRO`. |
| `details` | array (puede ser vacío) | sí (puede enviarse `[]`) | Daños de esa imagen puntual. Si se envía vacío, se dispara la detección automática (ver más abajo). |

Cada elemento de `details` (si se envían manualmente):

| Campo | Tipo | Obligatorio | Descripción |
|---|---|---|---|
| `detail_type` | string (enum `ImageDetailType`) | sí | Tipo de daño. Valores válidos: `ABOLLADURA`, `VIDRIO_ROTO`, `RAYON`, `GRIETA`, `ROTO`, `OXIDO`, `CALCOMANIA`, `PIEZA_FALTANTE`, `DANO_PINTURA`, `DEFORMACION`, `CHOQUE`, `OTRO_COLOR`, `OTRO`. |
| `description` | string (máx. 500 caracteres) | no | Descripción breve del daño. |

**retorna:**
```json
{
    "success": true,
    "message": "Vehículo creado correctamente.",
    "data": {
        "id": "8308f88e-55ac-46a0-8d41-7988f2d85248",
        "license_plate": "AA123BB",
        "brand": "Toyota",
        "model": "Corolla",
        "color": "Blanco",
        "year": 2020,
        "insurance_policy": "POL-000123",
        "observations": "Vehiculo de prueba",
        "is_active": true,
        "created_at": "2026-01-15T14:32:00Z",
        "updated_at": "2026-01-15T14:32:00Z",
        "images": [
            {
                "id": "3f9c1e2a-1234-4a5b-9c3d-1234567890ab",
                "filename": "a1b2c3d4-e5f6-7890-1234-567890abcdef.jpg",
                "image_url": "https://storage.googleapis.com/bucket/vehicles/8308f88e-55ac-46a0-8d41-7988f2d85248/a1b2c3d4-e5f6-7890-1234-567890abcdef.jpg",
                "label": "FRENTE",
                "embedding_status": "COMPLETADO",
                "details": [
                    {
                        "id": "7a1b2c3d-4e5f-6789-0abc-def123456789",
                        "detail_type": "RAYON",
                        "description": "Rayón leve en el paragolpes"
                    }
                ]
            },
            {
                "id": "9d8e7f6a-5b4c-3d2e-1f0a-987654321fed",
                "filename": "b2c3d4e5-f6a7-8901-2345-678901bcdefa.jpg",
                "image_url": "https://storage.googleapis.com/bucket/vehicles/8308f88e-55ac-46a0-8d41-7988f2d85248/b2c3d4e5-f6a7-8901-2345-678901bcdefa.jpg",
                "label": "ATRAS",
                "embedding_status": "PENDIENTE",
                "details": []
            }
        ]
    },
    "error": null
}
```

El significado de cada campo es el mismo que el detallado en `GET /vehicles`. En este ejemplo, la imagen "frente" ya trajo `details` manuales (por eso conserva `RAYON`) y quedó `embedding_status=COMPLETADO` (se indexó bien en el servicio de reconocimiento); la imagen "atras" llegó con `details: []` y quedó `embedding_status=PENDIENTE` (falló o no se llegó a indexar todavía, y será reintentada más adelante).

Si la patente ya existe → `409 CONFLICT`. Si `images` está vacío → `400 BAD_REQUEST`. Si los archivos enviados no coinciden exactamente con los `filename` de `images` (faltan archivos, sobran archivos, o ambos) → `400 BAD_REQUEST`, indicando en el mensaje cuáles faltan y cuáles sobran.

**Integración — best effort (detección automática de daños, OpenAI Vision):** por cada imagen cuyo `details` venga vacío (`[]` o campo omitido), el backend llama automáticamente a OpenAI Vision para detectar los daños visibles en esa foto puntual, pasándole el `label` (sector) como ancla de orientación — sin ese dato el modelo tiende a invertir izquierda/derecha en fotos laterales, ya que describe desde la perspectiva del espectador de la foto en vez de la del conductor. Si la imagen ya trae `details` explícitos, se respetan tal cual y **no** se llama a la IA para esa imagen puntual (override manual). Todas las detecciones se disparan en paralelo (una por imagen). Es best-effort: si la detección de una imagen falla, esa imagen queda simplemente con `details: []`, sin afectar el resto de la creación.

**Integración — best effort (indexación, servicio de reconocimiento):** tras persistir el vehículo, se envían las imágenes al servicio de reconocimiento (`POST /ingest`), con cada imagen llevando su propio `label` y `details` (ya resueltos, manuales o detectados por IA). Si la indexación falla (total o parcialmente), la creación del vehículo **no se revierte**: las imágenes que no pudieron indexarse quedan con `embedding_status=PENDIENTE` para ser reintentadas más adelante. Las que sí se indexan quedan con `embedding_status=COMPLETADO`, `embedding_id` y `indexed_at` seteados (estos dos últimos son internos, no se exponen en `VehicleResponse`).

---

**2- ruta:** `/vehicles/search/image`

**propósito:** busca vehículos visualmente similares a partir de una imagen.

**espera:** `multipart/form-data` con un único campo:

| Campo | Tipo | Obligatorio | Descripción |
|---|---|---|---|
| `file` | archivo | sí | La imagen a usar como base de la búsqueda. |

**retorna:**
```json
{
    "success": true,
    "message": "Búsqueda por imagen completada.",
    "data": {
        "threshold": 0.5638777,
        "matches": [
            {
                "vehicle": {
                    "id": "8308f88e-55ac-46a0-8d41-7988f2d85248",
                    "license_plate": "AA123BB",
                    "brand": "Toyota",
                    "model": "Corolla",
                    "color": "Blanco",
                    "year": 2020,
                    "insurance_policy": "POL-000123",
                    "observations": "Vehiculo de prueba",
                    "is_active": true,
                    "created_at": "2026-01-15T14:32:00Z",
                    "updated_at": "2026-01-15T14:32:00Z",
                    "images": [
                        {
                            "id": "3f9c1e2a-1234-4a5b-9c3d-1234567890ab",
                            "filename": "a1b2c3d4-e5f6-7890-1234-567890abcdef.jpg",
                            "image_url": "https://storage.googleapis.com/bucket/vehicles/8308f88e-55ac-46a0-8d41-7988f2d85248/a1b2c3d4-e5f6-7890-1234-567890abcdef.jpg",
                            "label": "FRENTE",
                            "embedding_status": "COMPLETADO",
                            "details": [
                                {
                                    "id": "7a1b2c3d-4e5f-6789-0abc-def123456789",
                                    "detail_type": "RAYON",
                                    "description": "Rayón leve en el paragolpes"
                                }
                            ]
                        },
                        {
                            "id": "9d8e7f6a-5b4c-3d2e-1f0a-987654321fed",
                            "filename": "b2c3d4e5-f6a7-8901-2345-678901bcdefa.jpg",
                            "image_url": "https://storage.googleapis.com/bucket/vehicles/8308f88e-55ac-46a0-8d41-7988f2d85248/b2c3d4e5-f6a7-8901-2345-678901bcdefa.jpg",
                            "label": "ATRAS",
                            "embedding_status": "PENDIENTE",
                            "details": []
                        }
                    ]
                },
                "score": 0.87,
                "matched_images": [
                    {
                        "label": "frente",
                        "score": 0.87,
                        "details": ["rayón puerta izquierda"]
                    }
                ]
            }
        ]
    },
    "error": null
}
```

Campos de la respuesta:

| Campo | Tipo | Descripción |
|---|---|---|
| `threshold` | float \| null | Umbral dinámico de aceptación calculado sobre la distribución de scores de esta búsqueda puntual. |
| `matches` | array | Vehículos encontrados, ordenados por relevancia según el servicio de reconocimiento. |
| `matches[].vehicle` | objeto | El vehículo completo, con la misma estructura detallada en `GET /vehicles`. |
| `matches[].score` | float | El mayor score entre todas las imágenes de ese vehículo que matchearon. |
| `matches[].matched_images` | array | Detalle de cada imagen puntual del vehículo que matcheó. |
| `matches[].matched_images[].label` | string | Sector de esa imagen puntual (tal como lo devuelve el servicio de reconocimiento, en minúsculas). |
| `matches[].matched_images[].score` | float | Score de similitud de esa imagen puntual. |
| `matches[].matched_images[].details` | array de strings | Daños de esa imagen puntual (como texto libre, tal como los almacenó el servicio de reconocimiento). |

Si el `vehicle_id` devuelto por el servicio de reconocimiento no existe en la base local (fue borrado), ese match se descarta silenciosamente (se loguea como warning) y no aparece en `matches`.

**Integración:** delega la búsqueda vectorial en `POST /search/image` del servicio de reconocimiento. Si esa llamada falla → `500 INTERNAL_SERVER_ERROR`.

---

**3- ruta:** `/vehicles/search/text`

**propósito:** búsqueda semántica híbrida por texto en lenguaje natural (ej: "vehiculo marca toyota modelo corolla color blanco con rayon en puerta izquierda").

**espera:** `multipart/form-data` (form field, no JSON) con un único campo:

| Campo | Tipo | Obligatorio | Descripción |
|---|---|---|---|
| `text` | string | sí | Consulta en lenguaje natural, en cualquier idioma (se traduce internamente al inglés antes de generar el embedding). |

**retorna:**
```json
{
    "success": true,
    "message": "Búsqueda por texto completada.",
    "data": {
        "threshold": 0.5638777,
        "matches": [
            {
                "vehicle": {
                    "id": "8308f88e-55ac-46a0-8d41-7988f2d85248",
                    "license_plate": "AA123BB",
                    "brand": "Toyota",
                    "model": "Corolla",
                    "color": "Blanco",
                    "year": 2020,
                    "insurance_policy": "POL-000123",
                    "observations": "Vehiculo de prueba",
                    "is_active": true,
                    "created_at": "2026-01-15T14:32:00Z",
                    "updated_at": "2026-01-15T14:32:00Z",
                    "images": [
                        {
                            "id": "3f9c1e2a-1234-4a5b-9c3d-1234567890ab",
                            "filename": "a1b2c3d4-e5f6-7890-1234-567890abcdef.jpg",
                            "image_url": "https://storage.googleapis.com/bucket/vehicles/8308f88e-55ac-46a0-8d41-7988f2d85248/a1b2c3d4-e5f6-7890-1234-567890abcdef.jpg",
                            "label": "FRENTE",
                            "embedding_status": "COMPLETADO",
                            "details": [
                                {
                                    "id": "7a1b2c3d-4e5f-6789-0abc-def123456789",
                                    "detail_type": "RAYON",
                                    "description": "Rayón leve en el paragolpes"
                                }
                            ]
                        },
                        {
                            "id": "9d8e7f6a-5b4c-3d2e-1f0a-987654321fed",
                            "filename": "b2c3d4e5-f6a7-8901-2345-678901bcdefa.jpg",
                            "image_url": "https://storage.googleapis.com/bucket/vehicles/8308f88e-55ac-46a0-8d41-7988f2d85248/b2c3d4e5-f6a7-8901-2345-678901bcdefa.jpg",
                            "label": "ATRAS",
                            "embedding_status": "PENDIENTE",
                            "details": []
                        }
                    ]
                },
                "score": 0.61,
                "matched_images": [
                    {
                        "label": "frente",
                        "score": 0.61,
                        "details": ["rayón puerta izquierda"]
                    }
                ]
            }
        ]
    },
    "error": null
}
```

El significado de cada campo de `matches` es el mismo que el detallado en `POST /vehicles/search/image`.

Si `text` viene vacío o solo espacios → `400 BAD_REQUEST`.

**Integración:** delega la búsqueda híbrida en `POST /search/text` del servicio de reconocimiento. Si esa llamada falla → `500 INTERNAL_SERVER_ERROR`.

Nota: esta búsqueda es por **similitud visual** (embeddings de las imágenes vía CLIP + boost por keywords en la metadata), no por filtros exactos de campos. Para eso último, ver `/vehicles/search/filters` a continuación.

---

**4- ruta:** `/vehicles/search/filters`

**propósito:** búsqueda estructurada por filtros exactos, extraídos automáticamente por IA a partir de una consulta en lenguaje natural (ej: "traeme todos los toyota corolla color blanco con choque atrás"). A diferencia de `search/image` y `search/text`, esta ruta **no** delega en el servicio de reconocimiento ni compara embeddings: traduce el texto a filtros y consulta directamente PostgreSQL.

**espera:** body JSON:

| Campo | Tipo | Obligatorio | Descripción |
|---|---|---|---|
| `text` | string (1 a 500 caracteres) | sí | Consulta en lenguaje natural. |

```json
{
    "text": "traeme todos los toyota corolla color blanco con choque atras"
}
```
Si `text` viene vacío o solo espacios → `400 BAD_REQUEST`.

**retorna:**
```json
{
    "success": true,
    "message": "Búsqueda por filtros completada.",
    "data": {
        "applied_filters": {
            "license_plate": null,
            "brand": "Toyota",
            "model": "Corolla",
            "color": "Blanco",
            "year": null,
            "insurance_policy": null,
            "label": "ATRAS",
            "detail_type": "CHOQUE"
        },
        "vehicles": [
            {
                "id": "8308f88e-55ac-46a0-8d41-7988f2d85248",
                "license_plate": "AA123BB",
                "brand": "Toyota",
                "model": "Corolla",
                "color": "Blanco",
                "year": 2020,
                "insurance_policy": "POL-000123",
                "observations": "Vehiculo de prueba",
                "is_active": true,
                "created_at": "2026-01-15T14:32:00Z",
                "updated_at": "2026-01-15T14:32:00Z",
                "images": [
                    {
                        "id": "3f9c1e2a-1234-4a5b-9c3d-1234567890ab",
                        "filename": "a1b2c3d4-e5f6-7890-1234-567890abcdef.jpg",
                        "image_url": "https://storage.googleapis.com/bucket/vehicles/8308f88e-55ac-46a0-8d41-7988f2d85248/a1b2c3d4-e5f6-7890-1234-567890abcdef.jpg",
                        "label": "ATRAS",
                        "embedding_status": "COMPLETADO",
                        "details": [
                            {
                                "id": "c4d5e6f7-8901-2345-6789-0abcdef12345",
                                "detail_type": "CHOQUE",
                                "description": "Impacto con chapa hundida en el paragolpes trasero"
                            }
                        ]
                    }
                ]
            }
        ]
    },
    "error": null
}
```

Campos de la respuesta:

| Campo | Tipo | Descripción |
|---|---|---|
| `applied_filters.license_plate` | string \| null | Patente interpretada por la IA, si el texto la mencionó. |
| `applied_filters.brand` | string \| null | Marca interpretada. |
| `applied_filters.model` | string \| null | Modelo interpretado. |
| `applied_filters.color` | string \| null | Color interpretado. |
| `applied_filters.year` | integer \| null | Año interpretado. |
| `applied_filters.insurance_policy` | string \| null | Póliza interpretada, solo si se menciona explícitamente. |
| `applied_filters.label` | string (enum `ImageLabel`) \| null | Sector del daño interpretado. |
| `applied_filters.detail_type` | string (enum `ImageDetailType`) \| null | Tipo de daño interpretado. |
| `vehicles` | array | Vehículos que cumplen todos los filtros aplicados, cada uno con la misma estructura completa detallada en `GET /vehicles`. Puede ser un array vacío si ningún vehículo matchea. |

`applied_filters` siempre se devuelve completo (los 8 campos), incluso si la mayoría quedaron en `null` — el usuario puede usarlo para ver cómo interpretó la IA su consulta y corregir si hizo falta. Si la IA no logra extraer ningún filtro (o la extracción falla), la búsqueda equivale a listar todos los vehículos (todos los campos de `applied_filters` en `null`).

**Detalle de cómo se aplica cada filtro:**
- `license_plate`, `brand`, `model`, `color`, `insurance_policy`: coincidencia parcial insensible a mayúsculas (`ILIKE`) contra las columnas del vehículo.
- `year`: igualdad exacta.
- `label` y `detail_type`: **no** son columnas del vehículo, sino atributos de sus imágenes. Se resuelven con un `EXISTS` correlacionado contra `vehicle_images` (y `image_details` cuando corresponde), exigiendo que **una misma imagen** cumpla ambas condiciones a la vez — así "choque atrás" requiere que exista una foto cuyo sector sea `ATRAS` Y que tenga ese daño puntual, no que el vehículo tenga por separado alguna foto de atrás y algún choque en cualquier otra imagen.
- El usuario nunca necesita conocer los nombres técnicos de los enums: la IA mapea lenguaje coloquial (ej. "hundimiento", "choque", "golpe fuerte") al `ImageDetailType`/`ImageLabel` más cercano usando una guía interna de sinónimos.

**Integración — best effort:** delega la extracción de filtros en OpenAI (Structured Outputs). Si la llamada falla, se loguea y se continúa **sin filtros** (equivale a listar todos los vehículos) en vez de devolver un error.

---

## PUT

**1- ruta:** `/vehicles/{vehicle_id}`

**propósito:** actualiza parcialmente los datos de un vehículo (cualquier subconjunto de campos).

**espera:** `vehicle_id` (path param, UUID) + body JSON con cualquier subconjunto de los siguientes campos (todos opcionales, pero debe enviarse al menos uno):

| Campo | Tipo | Descripción |
|---|---|---|
| `license_plate` | string (6 a 15 caracteres) | Nueva patente. |
| `brand` | string (1 a 50 caracteres) | Nueva marca. |
| `model` | string (1 a 50 caracteres) | Nuevo modelo. |
| `color` | string (máx. 50 caracteres) | Nuevo color. |
| `year` | integer (1900 a 2100) | Nuevo año. |
| `insurance_policy` | string (máx. 50 caracteres) | Nueva póliza. |
| `observations` | string (máx. 2000 caracteres) | Nuevas observaciones. |
| `is_active` | boolean | Nuevo estado de actividad. |

```json
{
    "brand": "Toyota",
    "model": "Corolla",
    "color": "Gris",
    "observations": "Actualizado via Postman"
}
```

**retorna:**
```json
{
    "success": true,
    "message": "Vehículo actualizado correctamente.",
    "data": {
        "id": "8308f88e-55ac-46a0-8d41-7988f2d85248",
        "license_plate": "AA123BB",
        "brand": "Toyota",
        "model": "Corolla",
        "color": "Gris",
        "year": 2020,
        "insurance_policy": "POL-000123",
        "observations": "Actualizado via Postman",
        "is_active": true,
        "created_at": "2026-01-15T14:32:00Z",
        "updated_at": "2026-01-15T15:10:00Z",
        "images": [
            {
                "id": "3f9c1e2a-1234-4a5b-9c3d-1234567890ab",
                "filename": "a1b2c3d4-e5f6-7890-1234-567890abcdef.jpg",
                "image_url": "https://storage.googleapis.com/bucket/vehicles/8308f88e-55ac-46a0-8d41-7988f2d85248/a1b2c3d4-e5f6-7890-1234-567890abcdef.jpg",
                "label": "FRENTE",
                "embedding_status": "COMPLETADO",
                "details": [
                    {
                        "id": "7a1b2c3d-4e5f-6789-0abc-def123456789",
                        "detail_type": "RAYON",
                        "description": "Rayón leve en el paragolpes"
                    }
                ]
            },
            {
                "id": "9d8e7f6a-5b4c-3d2e-1f0a-987654321fed",
                "filename": "b2c3d4e5-f6a7-8901-2345-678901bcdefa.jpg",
                "image_url": "https://storage.googleapis.com/bucket/vehicles/8308f88e-55ac-46a0-8d41-7988f2d85248/b2c3d4e5-f6a7-8901-2345-678901bcdefa.jpg",
                "label": "ATRAS",
                "embedding_status": "PENDIENTE",
                "details": []
            }
        ]
    },
    "error": null
}
```

El significado de cada campo es el mismo que el detallado en `GET /vehicles`. En este ejemplo, `color` y `observations` fueron los campos enviados en el body y quedaron reflejados con sus nuevos valores; el resto de los campos del vehículo permanece sin cambios.

Si `vehicle_id` no existe → `404 NOT_FOUND`. Si no se envía ningún campo → `400 BAD_REQUEST`. Si `license_plate` ya pertenece a otro vehículo → `409 CONFLICT`.

**Integración — best effort:** si cambian `brand`, `model`, `color` o `license_plate`, esos campos se replican en el servicio de reconocimiento vía `PATCH /vehicles/{vehicle_id}`, actualizando la metadata de todas las imágenes indexadas de ese vehículo. Si la llamada falla, se loguea pero **la actualización local ya persistida no se revierte**. `year`, `insurance_policy`, `observations` e `is_active` son propios del backend y no se replican (el servicio de reconocimiento no los conoce).

---

## PATCH

**1- ruta:** `/vehicles/{vehicle_id}/images/{image_id}/label`

**propósito:** actualiza el sector (`label`) de una imagen puntual.

**espera:** `vehicle_id` + `image_id` (path params, UUID) + body JSON:

| Campo | Tipo | Obligatorio | Descripción |
|---|---|---|---|
| `label` | string (enum `ImageLabel`) | sí | Nuevo sector. Valores válidos: `FRENTE`, `ATRAS`, `LATERAL_IZQUIERDA`, `LATERAL_DERECHA`, `FRENTE_IZQUIERDA`, `FRENTE_DERECHA`, `ATRAS_IZQUIERDA`, `ATRAS_DERECHA`, `OTRO`. |

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
    "data": {
        "id": "8308f88e-55ac-46a0-8d41-7988f2d85248",
        "license_plate": "AA123BB",
        "brand": "Toyota",
        "model": "Corolla",
        "color": "Blanco",
        "year": 2020,
        "insurance_policy": "POL-000123",
        "observations": "Vehiculo de prueba",
        "is_active": true,
        "created_at": "2026-01-15T14:32:00Z",
        "updated_at": "2026-01-15T14:32:00Z",
        "images": [
            {
                "id": "3f9c1e2a-1234-4a5b-9c3d-1234567890ab",
                "filename": "a1b2c3d4-e5f6-7890-1234-567890abcdef.jpg",
                "image_url": "https://storage.googleapis.com/bucket/vehicles/8308f88e-55ac-46a0-8d41-7988f2d85248/a1b2c3d4-e5f6-7890-1234-567890abcdef.jpg",
                "label": "LATERAL_IZQUIERDA",
                "embedding_status": "COMPLETADO",
                "details": [
                    {
                        "id": "7a1b2c3d-4e5f-6789-0abc-def123456789",
                        "detail_type": "RAYON",
                        "description": "Rayón leve en el paragolpes"
                    }
                ]
            },
            {
                "id": "9d8e7f6a-5b4c-3d2e-1f0a-987654321fed",
                "filename": "b2c3d4e5-f6a7-8901-2345-678901bcdefa.jpg",
                "image_url": "https://storage.googleapis.com/bucket/vehicles/8308f88e-55ac-46a0-8d41-7988f2d85248/b2c3d4e5-f6a7-8901-2345-678901bcdefa.jpg",
                "label": "ATRAS",
                "embedding_status": "PENDIENTE",
                "details": []
            }
        ]
    },
    "error": null
}
```

El significado de cada campo es el mismo que el detallado en `GET /vehicles`. En este ejemplo, la imagen `3f9c1e2a-...` es la que se identificó como `image_id` en el path, y su `label` pasó de `FRENTE` a `LATERAL_IZQUIERDA`; el resto de sus campos (incluyendo `details`) y el resto de las imágenes del vehículo quedan sin cambios.

Si la imagen no existe o no pertenece a `vehicle_id` → `404 NOT_FOUND`.

**Integración — best effort:** si la imagen tiene `embedding_id` (ya fue indexada), el nuevo label se traduce con `IMAGE_LABEL_TO_RECOGNITION_LABEL` y se replica vía `PATCH /update-label` del servicio de reconocimiento. Si la imagen no tiene `embedding_id` (nunca se indexó o quedó `PENDIENTE`), el cambio queda solo local. Si la llamada al servicio falla, se loguea pero el label local no se revierte.

---

**2- ruta:** `/vehicles/{vehicle_id}/images/{image_id}/file`

**propósito:** reemplaza el archivo de una imagen puntual, conservando su `label` y `details`.

**espera:** `vehicle_id` + `image_id` (path params, UUID) + `multipart/form-data`:

| Campo | Tipo | Obligatorio | Descripción |
|---|---|---|---|
| `file` | archivo | sí | La nueva imagen que reemplaza al archivo actual. |

**retorna:**
```json
{
    "success": true,
    "message": "Imagen reemplazada correctamente.",
    "data": {
        "id": "8308f88e-55ac-46a0-8d41-7988f2d85248",
        "license_plate": "AA123BB",
        "brand": "Toyota",
        "model": "Corolla",
        "color": "Blanco",
        "year": 2020,
        "insurance_policy": "POL-000123",
        "observations": "Vehiculo de prueba",
        "is_active": true,
        "created_at": "2026-01-15T14:32:00Z",
        "updated_at": "2026-01-15T14:32:00Z",
        "images": [
            {
                "id": "3f9c1e2a-1234-4a5b-9c3d-1234567890ab",
                "filename": "f9e8d7c6-b5a4-3210-9876-543210fedcba.jpg",
                "image_url": "https://storage.googleapis.com/bucket/vehicles/8308f88e-55ac-46a0-8d41-7988f2d85248/f9e8d7c6-b5a4-3210-9876-543210fedcba.jpg",
                "label": "FRENTE",
                "embedding_status": "COMPLETADO",
                "details": [
                    {
                        "id": "7a1b2c3d-4e5f-6789-0abc-def123456789",
                        "detail_type": "RAYON",
                        "description": "Rayón leve en el paragolpes"
                    }
                ]
            },
            {
                "id": "9d8e7f6a-5b4c-3d2e-1f0a-987654321fed",
                "filename": "b2c3d4e5-f6a7-8901-2345-678901bcdefa.jpg",
                "image_url": "https://storage.googleapis.com/bucket/vehicles/8308f88e-55ac-46a0-8d41-7988f2d85248/b2c3d4e5-f6a7-8901-2345-678901bcdefa.jpg",
                "label": "ATRAS",
                "embedding_status": "PENDIENTE",
                "details": []
            }
        ]
    },
    "error": null
}
```

El significado de cada campo es el mismo que el detallado en `GET /vehicles`. En este ejemplo, la imagen `3f9c1e2a-...` es la que se identificó como `image_id` en el path: su `filename` e `image_url` cambiaron para reflejar el nuevo archivo subido; `label` y `details` quedan exactamente igual que antes del reemplazo.

Si la imagen no existe o no pertenece a `vehicle_id` → `404 NOT_FOUND`.

**Integración:**
- Subida del nuevo archivo a Google Cloud Storage → **bloqueante** (si falla, se corta antes de tocar la base).
- Borrado del archivo anterior en Cloud Storage → **best effort** (si falla, se loguea; el archivo nuevo ya quedó persistido).
- Reemplazo del embedding en el servicio de reconocimiento (`PATCH /images/{embedding_id}`) → **best effort**, y solo si la imagen tenía `embedding_id`. El servicio de reconocimiento no vuelve a correr ANPR sobre la imagen nueva.

Nota: este endpoint **no** vuelve a correr la detección automática de daños sobre la imagen nueva. Los `details` existentes quedan sin cambios; para actualizarlos hay que editarlos manualmente (no existe hoy un endpoint dedicado a eso).

---

## DELETE

**1- ruta:** `/vehicles/{vehicle_id}`

**propósito:** elimina un vehículo junto con todas sus imágenes.

**espera:** `vehicle_id` (path param, UUID).

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

**espera:** `vehicle_id` + `image_id` (path params, UUID).

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

| Método | Ruta | Propósito | Integración externa |
|---|---|---|---|
| GET | `/vehicles` | Lista todos los vehículos | — |
| GET | `/vehicles/{vehicle_id}` | Obtiene un vehículo por id | — |
| GET | `/vehicles/patente/{license_plate}` | Obtiene un vehículo por patente | — |
| POST | `/vehicles` | Crea un vehículo con imágenes | OpenAI Vision (best effort, solo si faltan `details`) + `POST /ingest` (best effort) |
| POST | `/vehicles/search/image` | Busca por similitud visual (imagen) | `POST /search/image` |
| POST | `/vehicles/search/text` | Busca por similitud semántica (texto) | `POST /search/text` |
| POST | `/vehicles/search/filters` | Busca por filtros estructurados (texto → IA → SQL) | OpenAI (best effort, extracción de filtros) |
| PUT | `/vehicles/{vehicle_id}` | Actualiza datos del vehículo | `PATCH /vehicles/{vehicle_id}` (best effort) |
| PATCH | `/vehicles/{vehicle_id}/images/{image_id}/label` | Actualiza el label de 1 imagen | `PATCH /update-label` (best effort) |
| PATCH | `/vehicles/{vehicle_id}/images/{image_id}/file` | Reemplaza el archivo de 1 imagen | `PATCH /images/{embedding_id}` (best effort) |
| DELETE | `/vehicles/{vehicle_id}` | Elimina un vehículo completo | `DELETE /delete/{vehicle_id}` (estricto) |
| DELETE | `/vehicles/{vehicle_id}/images/{image_id}` | Elimina 1 imagen puntual | `DELETE /delete/embedding/{embedding_id}` (estricto, si existe) |

---

## Nota sobre inconsistencia entre GET y DELETE de imagen

Los endpoints de imagen (`update-label`, reemplazo de archivo, eliminación) usan `vehicle_id` + `image_id` en el path como sub-recurso de vehículo, ya que así está organizado el resto del router de `/vehicles`. Esto difiere del servicio de reconocimiento, que identifica las imágenes por `embedding_id` de forma plana (`/update-label`, `/images/{embedding_id}`, `/delete/embedding/{embedding_id}`). La traducción entre ambos identificadores (`image_id` local ↔ `embedding_id` remoto) la resuelve `VehicleService` internamente antes de llamar al servicio de reconocimiento.

## Nota sobre las dos búsquedas por texto

`/vehicles/search/text` y `/vehicles/search/filters` responden preguntas distintas aunque ambas acepten lenguaje natural:

- **`search/text`**: "¿qué vehículos se _parecen_ visual o semánticamente a esta descripción?" — usa embeddings CLIP y umbral dinámico, siempre delegado al servicio de reconocimiento.
- **`search/filters`**: "¿qué vehículos _cumplen exactamente_ con estos criterios?" — traduce la consulta a filtros discretos (marca, modelo, patente, sector, tipo de daño) y consulta PostgreSQL directamente, sin pasar por Qdrant.

Son complementarias: la primera es mejor para consultas ambiguas o basadas en apariencia, la segunda para consultas donde el usuario ya sabe exactamente qué campo busca pero no conoce el valor técnico exacto del enum.