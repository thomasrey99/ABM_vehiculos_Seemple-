# 🚗 Vehicle Management API

Backend REST desarrollado con **FastAPI** para la gestión inteligente de vehículos e imágenes.

El proyecto permite registrar vehículos, asociar múltiples imágenes con detalles específicos, detectar daños automáticamente mediante IA, y servir como base para un sistema de reconocimiento visual y búsqueda estructurada.

> ⚠️ El módulo de usuarios fue removido temporalmente del proyecto (se reincorporará más adelante). Crear un vehículo ya no requiere `owner_id`.

---

# 📌 Características

- Gestión completa de vehículos.
- Asociación de múltiples imágenes por vehículo, cada una con su `label` (sector) y sus `details` (daños).
- **Detección automática de daños por IA** (OpenAI Vision): si una imagen se sube sin `details`, el backend detecta los daños visibles automáticamente.
- **Búsqueda por filtros estructurados vía IA**: consultas en lenguaje natural traducidas a filtros exactos sobre la base (marca, modelo, color, patente, sector, tipo de daño), sin que el usuario conozca los nombres técnicos de los enums.
- Búsqueda por similitud visual (imagen) y semántica híbrida (texto), delegada al servicio de reconocimiento (CLIP + Qdrant).
- Almacenamiento de imágenes en Google Cloud Storage.
- Arquitectura por capas.
- SQLAlchemy Async.
- PostgreSQL.
- Validaciones con Pydantic V2.
- Manejo centralizado de excepciones.
- Respuestas API estandarizadas.
- Protección mediante API Key.

---

# 🏗 Arquitectura

```
app/
│
├── core/
│
├── db/
│
├── dependencies/
│
├── enums/
│
├── exceptions/
│
├── mappings/
│
├── models/
│
├── modules/
│   └── vehicles/
│
├── router.py
│
├── services/
│   ├── storage/
│   ├── recognition/
│   ├── damage_detection/
│   └── filter_extraction/
│
└── shared/
```

La aplicación sigue una arquitectura en capas:

```
Routes
   │
Controllers
   │
Services
   │
Repositories
   │
Database
```

Cada capa posee una única responsabilidad.

### 🧩 Servicios externos

Este backend orquesta dos integraciones externas, ambas encapsuladas detrás de interfaces (`RecognitionService`, `DamageDetectionService`, `FilterExtractionService`) para poder cambiar de proveedor sin tocar `VehicleService`:

- **ABM AI Service** (puerto 8001): embeddings CLIP + Qdrant, para búsqueda por imagen/texto.
- **OpenAI** (Vision + Structured Outputs): detección automática de daños y extracción de filtros desde lenguaje natural.

> Este repositorio se distribuye junto con `ABM_AI_service` en una única imagen Docker (ver `Dockerfile` y `start.sh` en la raíz del monorepo), que levanta ambos servicios en el mismo contenedor: backend en el puerto **8000**, servicio de IA en el **8001**.

---

# 🚀 Tecnologías

- Python 3.12 (imagen de producción/Docker) — desarrollo local probado también en 3.14.
- FastAPI
- SQLAlchemy 2.0
- PostgreSQL
- AsyncPG
- Pydantic V2
- Google Cloud Storage
- OpenAI API (GPT-4o / GPT-4o-mini, Structured Outputs)
- Uvicorn

---

# 📦 Instalación

Clonar el repositorio

```bash
git clone https://github.com/usuario/vehicle-management-api.git
```

Ingresar al proyecto

```bash
cd ABM_backend
```

Crear entorno virtual

Windows

```bash
python -m venv .venv
```

Linux

```bash
python3 -m venv .venv
```

Activar entorno

Windows

```bash
.venv\Scripts\activate
```

Linux

```bash
source .venv/bin/activate
```

Instalar dependencias

```bash
pip install -r requirements.txt
```

---

# ⚙ Variables de entorno

Crear un archivo

```
.env
```

Ejemplo:

```env
# Base de datos
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/vehicles

# Seguridad
SERVICE_API_KEY=tu_api_key

# Google Cloud Storage
GOOGLE_CLOUD_PROJECT_ID=...
GOOGLE_CLOUD_BUCKET=...
GOOGLE_APPLICATION_CREDENTIALS=credentials/google_cloud_credentials.json

# Servicio de reconocimiento (ABM AI Service)
AI_SERVICE_URL=http://localhost:8001
AI_SERVICE_API_KEY=tu_api_key_del_servicio_de_ia
AI_SERVICE_TIMEOUT=60

# Detección de daños / extracción de filtros (OpenAI)
OPENAI_API_KEY=sk-...
OPENAI_DAMAGE_MODEL=gpt-4o
OPENAI_FILTER_MODEL=gpt-4o-mini
```

> `AI_SERVICE_API_KEY` debe coincidir con el `SERVICE_API_KEY` configurado en `ABM_AI_service`.

---

# ▶ Ejecutar el proyecto

```bash
uvicorn main:app --reload
```

La documentación estará disponible en:

Swagger

```
http://localhost:8000/docs
```

Redoc

```
http://localhost:8000/redoc
```

---

# 🔐 Autenticación

Todos los endpoints se encuentran protegidos mediante API Key.

Enviar el header:

```
X-API-Key
```

Ejemplo

```
X-API-Key: my-secret-key
```

---

# 🚙 Módulo Vehículos

## Crear vehículo

```
POST /vehicles
```

Recibe información del vehículo, imágenes y detalles de cada imagen mediante `multipart/form-data`.

Si una imagen se envía con `details: []` (o el campo omitido), el backend dispara automáticamente la detección de daños vía IA (OpenAI Vision) para esa imagen puntual, usando el `label` (sector) como referencia de orientación. Si el cliente ya envía `details` manuales, esos se respetan tal cual y no se llama a la IA para esa imagen. Es best-effort por imagen: si la detección falla, esa imagen queda simplemente sin `details`.

---

## Obtener vehículos

```
GET /vehicles
```

## Obtener vehículo por id

```
GET /vehicles/{vehicle_id}
```

## Obtener vehículo por patente

```
GET /vehicles/patente/{license_plate}
```

## Actualizar vehículo

```
PUT /vehicles/{vehicle_id}
```

## Eliminar vehículo

```
DELETE /vehicles/{vehicle_id}
```

---

## 🔎 Búsqueda

```
POST /vehicles/search/image     → similitud visual (CLIP + Qdrant)
POST /vehicles/search/text      → búsqueda semántica híbrida (texto + boost por metadata)
POST /vehicles/search/filters   → filtros estructurados extraídos por IA (brand, model, color, patente, año, póliza, sector, tipo de daño)
```

`search/filters` es distinto de `search/text`: no busca por similitud visual, sino que traduce la consulta a filtros exactos y consulta directamente contra PostgreSQL (con `EXISTS` correlacionado para `label`+`detail_type`, garantizando que ambos condicionen la misma imagen). La respuesta incluye `applied_filters`, para que el cliente vea cómo interpretó la IA su consulta.

---

# 📸 Gestión de imágenes

Cada vehículo puede poseer múltiples imágenes.

Cada imagen contiene:

- `label` (sector: frente, lateral, trasera, etc. — ver `ImageLabel`)
- `image_url` / `filename`
- `embedding_status` (estado de indexación en el servicio de reconocimiento)
- `details` (daños detectados, manuales o por IA)

Ejemplo:

```
Vehículo

 ├── Frente
 │     ├── Rayón
 │     └── Abolladura
 │
 ├── Trasera
 │     └── Sin detalles
 │
 └── Lateral Izquierdo
       ├── Golpe
       └── Pintura
```

Endpoints adicionales de imagen:

```
PATCH /vehicles/{vehicle_id}/images/{image_id}/label   → cambia el sector de una imagen
PATCH /vehicles/{vehicle_id}/images/{image_id}/file    → reemplaza el archivo de una imagen
DELETE /vehicles/{vehicle_id}/images/{image_id}        → elimina una imagen puntual
```

Ver `routes_info.md` para el detalle completo de cada endpoint (request/response, modo de integración con el servicio de reconocimiento, códigos de error).

---

# 🗄 Base de datos

Principales entidades

```
Vehicle
```

```
VehicleImage
```

```
ImageDetail
```

Relaciones

```
Vehicle
   │
   └──────── VehicleImage
                    │
                    └────── ImageDetail
```

---

# 📂 Almacenamiento

Las imágenes son almacenadas en

```
Google Cloud Storage
```

Cada imagen conserva:

- filename
- url
- label
- details

---

# 📋 Respuesta de la API

Todas las respuestas siguen el mismo formato.

Éxito

```json
{
    "success": true,
    "message": "Operation successful",
    "data": {},
    "error": null
}
```

Error

```json
{
    "success": false,
    "message": "Vehicle not found",
    "data": null,
    "error": "NOT_FOUND"
}
```

---

# ⚠ Manejo de errores

La API implementa excepciones personalizadas.

- BadRequestException
- NotFoundException
- ConflictException
- UnauthorizedException
- InternalServerException

Todas son manejadas mediante Exception Handlers globales.

---

# ✅ Validaciones

Se utilizan modelos Pydantic V2.

Entre las validaciones se incluyen:

- UUID válidos
- Longitud de cadenas
- Año permitido
- Campos obligatorios
- Validación de imágenes (los `filename` en `request.images[]` deben coincidir exactamente con los archivos subidos)
- Validación de patente única

---

# 🔄 Flujo de creación de un vehículo

```
Cliente

    │

POST /vehicles

    │

Controller

    │

VehicleService

    │

Validar patente

    │

Resolver details (manual o detección automática de daños vía IA, en paralelo por imagen)

    │

Subir imágenes a Google Cloud Storage

    │

Crear entidad Vehicle + imágenes + detalles

    │

Persistir en PostgreSQL

    │

Indexar imágenes en el servicio de reconocimiento (best effort, no bloquea la respuesta)

    │

Retornar VehicleResponse
```

---

# 🔮 Próximas funcionalidades

- Reincorporar el módulo de Usuarios.
- `GET /vehicles/enums`, para exponer dinámicamente los valores válidos de los enums a agentes/clientes.
- Columnas `source` (MANUAL / IA) y `confidence` en `ImageDetail`, para distinguir daños verificados por humanos de los inferidos por IA (relevante por implicancias de responsabilidad en el contexto de seguros).
- Soft Delete.
- Auditoría.
- Tests automatizados.
- CI/CD.

---

# 📄 Licencia

Este proyecto fue desarrollado con fines educativos y de demostración técnica.

Puede ser utilizado como base para proyectos comerciales o académicos.

---

# 👨‍💻 Autor

**Thomas Leonel Rey**

Backend Developer

FastAPI • PostgreSQL • SQLAlchemy • Python