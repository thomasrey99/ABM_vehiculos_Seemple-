# ABM AI Service — Reconocimiento y Búsqueda de Imágenes de Vehículos

Servicio en FastAPI para indexar y buscar imágenes de vehículos por similitud visual (CLIP), por patente (ANPR) y por descripción en lenguaje natural (búsqueda semántica híbrida). Usa **Qdrant** como base de datos vectorial.

> Este proyecto ya NO es polimórfico (no es genérico para cualquier entidad) — está orientado específicamente a vehículos.

## Stack tecnológico

- **FastAPI** — framework web.
- **CLIP** (vía `sentence-transformers`) — genera embeddings de imágenes y texto en un espacio semántico compartido.
- **Qdrant** — base de datos vectorial, almacena embeddings + metadata (payload).
- **fast-alpr** (ONNX) — reconocimiento automático de patentes (ANPR), usado en la búsqueda por imagen.
- **deep-translator** (Google Translate) — traduce las consultas de texto al inglés antes de generar el embedding, porque CLIP entiende mejor ese idioma.
- **OpenCV** — decodificación de imágenes para el módulo de ANPR.

## Variables de entorno (`.env`)

| Variable | Descripción | Default |
|---|---|---|
| `SERVICE_API_KEY` | Clave requerida en el header `X-API-Key` para todas las rutas | *(requerida)* |
| `QDRANT_URL` | URL de la instancia de Qdrant | *(requerida)* |
| `QDRANT_API_KEY` | API key de Qdrant | *(requerida)* |
| `MODEL` | Nombre/ruta del modelo CLIP (SentenceTransformer) | *(requerida)* |
| `COLLECTION_NAME` | Nombre de la colección en Qdrant | `vehicles-images` |
| `CLIP_VECTOR_SIZE` | Dimensión del vector de embedding | `512` |
| `VECTOR_DISTANCE` | Métrica de distancia (`Cosine`, `Euclidean`, `Dot`) | `Cosine` |
| `PLATE_MIN_CONFIDENCE` | Confianza mínima del OCR de patente para aceptar una lectura | `0.90` |
| `PLATE_DETECTOR_MODEL` | Modelo detector de patentes (fast-alpr) | `yolo-v9-t-384-license-plate-end2end` |
| `PLATE_OCR_MODEL` | Modelo OCR de patentes (fast-alpr) | `cct-xs-v2-global-model` |

⚠️ **Ojo con `COLLECTION_NAME`**: si tu `.env` apunta a una colección vieja (ej. de una etapa anterior del proyecto), vas a leer/escribir contra datos con un esquema distinto sin ningún error visible. Verificá que coincida con la colección real que estás usando en la UI de Qdrant.

## Cómo correr

```bash
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8001
```

O con Docker:
```bash
docker build -t abm-ai-service .
docker run -p 8001:8001 --env-file .env abm-ai-service
```

Todas las rutas requieren el header `X-API-Key: <tu SERVICE_API_KEY>`.

## Estructura del proyecto

```
app/
├── config/settings.py              # Configuración (.env) tipada con pydantic-settings
├── core/
│   ├── model_embedding.py          # Singleton del modelo CLIP
│   ├── plate_model.py              # Singleton del modelo ANPR (fast-alpr)
│   └── security.py                 # Validación de X-API-Key
├── db/
│   ├── qdrant_client.py            # Clientes sync/async de Qdrant
│   └── init_db.py                  # Creación de colección + índices de payload
├── exceptions/
│   ├── appExceptions.py            # AppException, BadRequestException, InternalServerException, NotFoundException
│   └── handlers.py                 # Handlers globales de excepciones
├── schemas/
│   ├── request.py                  # UpdateLabelRequest, UpdateVehicleRequest, IngestMetadata, ImageIngestData
│   ├── response.py                 # APIResponse[T], IndexedImageResponse
│   └── vehicle_schemas.py          # ImageMatch, VehiclesGroup, SearchResponse
├── services/
│   ├── embedding/embedding_service.py   # Genera embeddings (texto o imagen) con CLIP
│   └── qdrant/
│       ├── vector_save_service.py       # Upsert de un punto (embedding + payload)
│       ├── vector_search_service.py     # Búsqueda por similitud + búsqueda exacta por patente
│       ├── vector_get_service.py        # Obtener un punto por id
│       ├── vector_replace_service.py    # Reemplazar el embedding de un punto
│       ├── vector_delete_service.py     # Borrado por vehicle_id o por lista de ids
│       └── vector_update_metadata_service.py  # Update masivo de metadata por vehicle_id
├── utils/
│   ├── preprocess_image.py         # Preprocesa imágenes para CLIP (EXIF, RGB, resize)
│   ├── plate_recognition.py        # Detección/lectura de patente (ANPR) sobre imagen cruda
│   ├── traduction.py               # Traduce texto al inglés (deep_translator)
│   ├── query_keywords.py           # Extrae keywords de una consulta en lenguaje natural
│   ├── text_normalize.py           # Normaliza texto (minúsculas, sin tildes)
│   ├── keyword_boost.py            # Calcula el boost de score por coincidencia de keywords
│   ├── group_results.py            # Agrupa resultados de Qdrant por vehicle_id
│   ├── dynamic_threshold.py        # Umbral de aceptación calculado sobre la distribución de scores
│   └── response.py                 # build_response() — formato estándar de respuesta
├── controllers/
│   ├── post/    (ingest, search_image, search_text)
│   ├── patch/   (update_label, replace_image, update_vehicle)
│   └── delete/  (delete_vehicle, delete_embedding)
└── routes/      (mismo árbol que controllers, un archivo por endpoint)
```

## Modelo de datos (payload en Qdrant)

Cada punto en Qdrant representa **una imagen** de un vehículo:

```json
{
    "vehicle_id": "<uuid>",
    "label": "atras",
    "details": ["abolladura", "vidrio roto"],
    "license_plate": "AA021ID",
    "brand": "Toyota",
    "model": "Corolla",
    "color": "Blanco"
}
```

- `vehicle_id`, `brand`, `model`, `color`, `license_plate`: **compartidos** por todas las imágenes del mismo vehículo.
- `label`: **una sola etiqueta por imagen** (el sector fotografiado: frente, atrás, lateral izquierda, etc.).
- `details`: **cero o más** por imagen (una foto puede mostrar abolladura Y vidrio roto a la vez).

## Endpoints

| Método | Ruta | Propósito |
|---|---|---|
| POST | `/ingest` | Sube e indexa un lote de imágenes de un vehículo (patente manual) |
| POST | `/search/image` | Busca por imagen — primero intenta match exacto por patente (ANPR), si no usa similitud visual |
| POST | `/search/text` | Búsqueda semántica híbrida por texto en lenguaje natural |
| PATCH | `/update-label` | Actualiza el label (sector) de una imagen puntual |
| PATCH | `/images/{embedding_id}` | Reemplaza la imagen/embedding de un punto existente |
| PATCH | `/vehicles/{vehicle_id}` | Actualiza brand/model/color/license_plate de todo el vehículo |
| DELETE | `/delete/{vehicle_id}` | Elimina todas las imágenes de un vehículo |
| DELETE | `/delete/embedding/{embedding_id}` | Elimina una imagen puntual |

Formato completo de request/response de cada uno: ver `rutas_informe.md` (o la colección de Postman `consultas_postman.json`).

## Flujos clave

### Reconocimiento de patente (ANPR)
Se usa **exclusivamente en `/search/image`**, nunca en la ingesta (la patente se carga manualmente al ingestar). Al buscar por imagen:
1. Se corre `fast-alpr` sobre la imagen cruda (sin el resize de CLIP, para no perder legibilidad).
2. Si detecta una patente con confianza ≥ `PLATE_MIN_CONFIDENCE` (90% por defecto), busca match **exacto** de esa patente en el payload y devuelve el vehículo directamente (sin comparar embeddings).
3. Si no hay patente confiable, o ningún vehículo la tiene, cae al flujo de similitud visual con umbral dinámico.

### Búsqueda semántica híbrida por texto
Combina dos señales, sin usar ninguna como filtro excluyente:
1. **Similitud visual-semántica**: el texto se traduce al inglés (`deep_translator`) y se compara vía CLIP contra los embeddings de las imágenes, sin piso de score duro (los scores texto↔imagen son naturalmente más bajos que imagen↔imagen).
2. **Boost por metadata**: se extraen keywords del texto **original** (sin traducir) y se les suma puntaje a los resultados cuyo `label`/`details`/`brand`/`model`/`color` las contengan — calculado **por imagen individual**, antes de agrupar por vehículo, para que "rayón en la puerta izquierda" priorice justo la foto de ese sector.

El umbral de aceptación final (`compute_dynamic_threshold`) se calcula sobre los scores ya combinados (visual + boost).

## Notas de diseño

- **Rollback en `/ingest`**: si falla una imagen a mitad del lote, se revierten (`delete`) los puntos ya insertados en ese request, para no dejar datos parciales.
- **`label` vs `details`**: una imagen tiene un único sector (`label`) pero puede tener varios detalles (`details`) — es una relación 1-a-N, reflejada en el schema `ImageIngestData` de la ingesta.
- **`/search/filtered` fue removido**: la búsqueda híbrida por texto (con boost por `label`) cubre los casos de sector específico con más flexibilidad que un filtro estricto por etiquetas.

## Pendiente / mejoras conocidas

- El modelo CLIP (`model.encode`) y el modelo ANPR corren de forma **síncrona**, bloqueando el event loop de FastAPI bajo carga concurrente. Recomendado: envolverlos en threadpool (`anyio.to_thread.run_sync`).
- `deep-translator` depende de un servicio no oficial (Google Translate) sin caché ni timeout propio — puede fallar o rate-limitear bajo volumen.
- Verificar que `deep-translator` esté explícitamente en `requirements.txt` (se usa en `app/utils/traduction.py` pero no estaba listado en la versión original del archivo).