# 🚗 Vehicle Management API

Backend REST desarrollado con **FastAPI** para la gestión inteligente de vehículos e imágenes.

El proyecto permite registrar vehículos, asociar múltiples imágenes con detalles específicos, administrar propietarios y servir como base para un sistema de reconocimiento visual mediante IA.

---

# 📌 Características

- Gestión completa de usuarios.
- Gestión completa de vehículos.
- Asociación de múltiples imágenes por vehículo.
- Registro de detalles por imagen.
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
├── models/
│
├── modules/
│   ├── users/
│   └── vehicles/
│
├── router.py
│
├── services/
│   └── storage/
│
└── utils/
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

---

# 🚀 Tecnologías

- Python 3.14
- FastAPI
- SQLAlchemy 2.0
- PostgreSQL
- AsyncPG
- Alembic
- Pydantic V2
- Google Cloud Storage
- Uvicorn

---

# 📦 Instalación

Clonar el repositorio

```bash
git clone https://github.com/usuario/vehicle-management-api.git
```

Ingresar al proyecto

```bash
cd vehicle-management-api
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
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/vehicles

SERVICE_API_KEY=tu_api_key

GOOGLE_CLOUD_PROJECT=...

GOOGLE_CLOUD_BUCKET=...

GOOGLE_APPLICATION_CREDENTIALS=credentials.json
```

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

# 📁 Módulo Usuarios

## Crear usuario

```
POST /users
```

## Obtener usuarios

```
GET /users
```

## Obtener usuario

```
GET /users/{id}
```

## Actualizar usuario

```
PUT /users/{id}
```

## Eliminar usuario

```
DELETE /users/{id}
```

---

# 🚙 Módulo Vehículos

## Crear vehículo

```
POST /vehicles
```

El endpoint recibe:

- información del vehículo
- imágenes
- detalles de cada imagen

mediante

```
multipart/form-data
```

---

## Obtener vehículos

```
GET /vehicles
```

---

## Obtener vehículo

```
GET /vehicles/{id}
```

---

## Actualizar vehículo

```
PUT /vehicles/{id}
```

---

## Eliminar vehículo

```
DELETE /vehicles/{id}
```

---

# 📸 Gestión de imágenes

Cada vehículo puede poseer múltiples imágenes.

Cada imagen contiene:

- etiqueta (frente, lateral, trasera, etc.)
- URL
- detalles

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

---

# 🗄 Base de datos

Principales entidades

```
User
```

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
User
  │
  └────────── Vehicle
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
- tipo
- detalles

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
- Validación de imágenes
- Validación de propietario
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

Validar propietario

    │

Validar patente

    │

Subir imágenes a Google Cloud Storage

    │

Crear entidad Vehicle

    │

Crear imágenes

    │

Crear detalles

    │

Persistir en PostgreSQL

    │

Retornar VehicleResponse
```

---

# 🔮 Próximas funcionalidades

- Reconocimiento automático de patentes (ALPR)
- Búsqueda de vehículos mediante imágenes
- Embeddings con modelos de visión
- Integración con Qdrant
- Búsqueda por similitud visual
- Actualización avanzada de imágenes
- Soft Delete
- Auditoría
- Docker
- CI/CD
- Tests automatizados

---

# 📄 Licencia

Este proyecto fue desarrollado con fines educativos y de demostración técnica.

Puede ser utilizado como base para proyectos comerciales o académicos.

---

# 👨‍💻 Autor

**Thomas Leonel Rey**

Backend Developer

FastAPI • PostgreSQL • SQLAlchemy • Python