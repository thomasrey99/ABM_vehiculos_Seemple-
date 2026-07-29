# API de Reconocimiento de Imágenes Multimodal 🏠🔍

Este proyecto es un microservicio de Inteligencia Artificial diseñado para la indexación y búsqueda multimodal de imágenes (por similitud visual y texto). 
Utiliza el modelo **CLIP** para la generación de embeddings, **Qdrant** como base de datos vectorial y **FastAPI** para la gestión robusta de rutas.

---

## 📋 Requisitos Previos

* **Docker** y **Docker Compose** (Recomendado para el despliegue y desarrollo).
* **Python 3.10+** (Si se desea ejecutar localmente sin Docker).
* Una instancia de **Qdrant** (Local a través de Docker o Qdrant Cloud).

---

## 📁 Estructura del Proyecto
La arquitectura sigue el patrón **MVC** (Modelo-Vista-Controlador) para asegurar la escalabilidad y el desacoplamiento de la lógica de IA.

```bash
Servicio-de-reconocimiento-de-imagenes/
 ├── 📂 app/                  # Código fuente de la aplicación
 │    ├── 🎮 controllers/    # Orquestación y validación de entrada
 │    ├── 🤖 services/       # Integraciones (CLIP, Qdrant)
 │    ├── 📦 schemas/        # Modelos Pydantic (Estructuras de datos)
 │    ├── 🔑 core/           # Configuración de modelos y seguridad
 │    ├── 🗄️ db/             # Clientes e inicialización de BD
 │    ├── 🛠️ utils/          # Herramientas de soporte y preprocesamiento
 │    └── 🛣️ routes/         # Definición de endpoints FastAPI
 ├── 📂 __pycache__/         # Archivos de caché de Python (Excluidos en .gitignore)
 ├── 📂 venv/                # Entorno virtual de Python (Excluidos en .gitignore)
 ├── 🐳 .dockerignore        # Archivos excluidos del contexto de Docker
 ├── 📄 .env                 # Variables de entorno (No incluido en Git)
 ├── 📄 .env.example         # Plantilla de variables de entorno
 ├── 📄 .gitignore           # Archivos excluidos del repositorio Git
 ├── 🚀 consultas_postman.json # Colección de pruebas para endpoints
 ├── 🐳 docker-compose.yml   # Orquestación de contenedores
 ├── 🐳 Dockerfile           # Receta para la imagen de la API
 ├── 🐍 main.py              # Punto de entrada de la aplicación FastAPI
 ├── 📄 README.md            # Documentación del proyecto
 └── 📄 requirements.txt     # Dependencias de Python
```

---

## ⚙️ Configuración del Entorno (`.env`)

El microservicio requiere de ciertas variables de entorno para inicializar la conexión con la base de datos, configurar el modelo de IA y establecer la seguridad. 

Crea un archivo llamado `.env` en la raíz del proyecto (puedes duplicar el archivo `.env.example` para usarlo como plantilla) y completa los valores.

> ⚠️ **SEGURIDAD:** Nunca hagas *commit* ni subas tu archivo `.env` a repositorios públicos (GitHub/GitLab). Asegúrate de que esté incluido en tu archivo `.gitignore`.

### 📖 Diccionario de Variables

| Variable | Categoría | Descripción | Ejemplo / Default |
| :--- | :---: | :--- | :--- |
| **`SERVICE_API_KEY`** | 🔐 Seguridad | Llave maestra que protegerá tus endpoints. Todo cliente que consuma esta API debe enviarla. | `mi_clave_secreta_123` |
| **`MODEL`** | 🧠 Modelo IA | Nombre del modelo CLIP de HuggingFace/SentenceTransformers a instanciar. | `clip-ViT-B-32` |
| **`CLIP_VECTOR_SIZE`** | 🧠 Modelo IA | Tamaño de las dimensiones del vector que escupe el modelo. | `512` |
| **`VECTOR_DISTANCE`** | 🧠 Modelo IA | Métrica matemática que usará Qdrant para calcular la similitud. | `Cosine` |
| **`COLLECTION_NAME`** | 💾 Qdrant | Nombre de la colección donde se indexarán las imágenes. | `properties-images` |
| **`QDRANT_URL`** | 💾 Qdrant | Dirección URL (Endpoint) de tu clúster de base de datos vectorial. | `https://[id].cloud.qdrant.io` |
| **`QDRANT_API_KEY`** | 💾 Qdrant | Token de acceso (solo requerido si utilizas Qdrant Cloud). | `eyJhbGciOi...` |

### 📄 Plantilla para copiar y pegar

```env
# ==========================================
# 🔐 SEGURIDAD
# ==========================================
SERVICE_API_KEY=tu_clave_super_secreta

# ==========================================
# 🧠 CONFIGURACIÓN DEL MODELO DE IA (CLIP)
# ==========================================
MODEL=clip-ViT-B-32
CLIP_VECTOR_SIZE=512
VECTOR_DISTANCE=Cosine

# ==========================================
# 💾 CONFIGURACIÓN DE QDRANT
# ==========================================
COLLECTION_NAME=properties-images
QDRANT_URL=[https://tu-url-de-qdrant.cloud.qdrant.io](https://tu-url-de-qdrant.cloud.qdrant.io)
QDRANT_API_KEY=tu_qdrant_api_key

```

---

## 🚀 Instalación y Ejecución

### Opción A: Usando Docker Compose (Recomendado)

La forma más rápida, segura y estandarizada de levantar el proyecto junto con todas sus dependencias. Asegúrate de tener tu archivo `.env` configurado.

Ejecuta el siguiente comando en tu terminal:

```bash
docker compose up -d --build
```

El servicio estará disponible en 👉 `http://localhost:8000`.

**NOTA**: Debido al peso de las dependencias, es normal que demore en completarse el proceso, suele tardar alrededor de 20 min con una buena conexion a internet, no interrumpas el proceso hasta que veas el build success.

### Opción B: Ejecución Manual (Desarrollo Local sin Docker)

**1. Crea un entorno virtual e instala las dependencias:**

```bash
# Crear entorno
python -m venv venv

# Activar entorno (Linux/macOS)
source venv/bin/activate  

# Activar entorno (Windows)
venv\Scripts\activate     

# Instalar requerimientos
pip install -r requirements.txt
```

**2. Ejecuta el servidor con Uvicorn** (con recarga en caliente para desarrollo):

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

---

## 🔐 Autenticación (Seguridad M2M)

Todas las rutas de escritura y lectura de esta API están protegidas. Para consumir cualquier endpoint, debes incluir obligatoriamente la llave de seguridad en los **Headers** de tu petición HTTP:

* **Header Key:** `X-API-Key`
* **Value:** `<SERVICE_API_KEY>` *(El valor exacto definido en tu archivo .env)*

---

## 🌐 Documentación Interactiva (Swagger UI)

Una vez que el servidor esté corriendo, puedes acceder a la documentación interactiva autogenerada por FastAPI navegando a: 
👉 **[http://localhost:8000/docs](http://localhost:8000/docs)**

Allí podrás probar todos los endpoints directamente desde el navegador. Recuerda hacer clic en el botón verde **"Authorize"** en la parte superior derecha para ingresar tu API Key antes de hacer peticiones.

---

## 🛠️ Contrato de Respuesta (Estructura Base)

Todas las rutas devuelven sistemáticamente la siguiente estructura base de respuesta, lo que facilita la integración con el frontend o el backend principal:

```json
{
    "success": true | false,
    "message": "Mensaje descriptivo sobre la operación",
    "data": { ... } | null,
    "error": "TIPO_DE_ERROR" | null
}
```

---

## 🛣️ Uso de las Rutas (Endpoints)

> **Nota:** Todas las rutas utilizan `multipart/form-data` para recibir los parámetros y archivos.

### 1. Ingesta de Imágenes (Subir Propiedad)
Indexa fotos asociadas a una propiedad. Para garantizar que los filtros de búsqueda ("Street View") funcionen correctamente, es **obligatorio** respetar la siguiente taxonomía estricta para el campo `labels`.

* **Ruta:** `POST /ingest`
* **Formato:** `multipart/form-data`

| Campo | Tipo | Descripción |
| :--- | :--- | :--- |
| `parent_id` | `UUID` | ID único de la propiedad. |
| `files` | `File[]` | Lista de imágenes a indexar. |
| `labels` | `String[]`| Etiquetas de la taxonomía (deben coincidir en cantidad con los archivos). |

### 🏷️ Taxonomía Estándar de Vistas (labels)

* **Nota**: Es importante respetar esta taxonomía para mejorar la precisión de las búsquedas filtradas por etiquetas (Street View). Cada imagen debe tener una etiqueta que describa la vista específica de la propiedad.



| Etiqueta Exacta | Descripción de la Fotografía |
| :--- | :--- |
| `frente` | Vista frontal directa a la fachada de la propiedad. |
| `frente 45 izquierda` | Vista en diagonal (45º) tomada desde el lado izquierdo. |
| `frente 45 derecha` | Vista en diagonal (45º) tomada desde el lado derecho. |
| `lateral izq` | Vista completamente de perfil desde el lado izquierdo. |
| `lateral der` | Vista completamente de perfil desde el lado derecho. |
| `atras` | Vista desde la parte trasera. |


**NOTA** : La primera etiqueta del array corresponde al primer archivo del array, y así sucesivamente.

#### ✅ Respuesta Exitosa
```json
{
    "success": true,
    "message": "Imágenes indexadas correctamente para la entidad 123e4567-e89b-12d3-a456-426614174001",
    "data": [
        {
            "parent_id": "123e4567-e89b-12d3-a456-426614174001",
            "vector_id": "d4f372c5-c198-4cc6-82de-f40ca215fb7f",
            "label": "frente"
        },
        {
            "parent_id": "123e4567-e89b-12d3-a456-426614174001",
            "vector_id": "0f97b38b-3798-4599-b7d0-6f6c7e92a067",
            "label": "frente 45 izquierda"
        },
        {
            "parent_id": "123e4567-e89b-12d3-a456-426614174001",
            "vector_id": "d21cba6d-ef82-4d93-be5f-e7875ccd13b0",
            "label": "frente 45 derecha"
        }
    ],
    "error": null
}
```

---

### 🖼️ 2. Búsqueda Genérica (Solo Imagen)
Busca propiedades similares a la imagen proporcionada evaluando únicamente la similitud visual. El sistema utiliza un **umbral de coincidencia dinámico** para garantizar la relevancia de los resultados.

* **Método:** `POST`
* **Ruta:** `/search/image`
* **Formato:** `multipart/form-data`

| Campo | Tipo | Descripción |
| :--- | :--- | :--- |
| `file` | `File` | La imagen base utilizada para calcular la similitud vectorial. |

#### ✅ Respuesta Exitosa (Data)

```json
{
    "success": true,
    "message": "Busqueda de imagen completada",
    "data": {
        "matches": [
            {
                "parent_id": "123e4567-e89b-12d3-a456-426614174000",
                "images": [
                    {
                        "score": 1.0,
                        "label": "frente"
                    },
                    {
                        "score": 0.98,
                        "label": "frente 45 izquierda"
                    }
                ]
            }
        ],
        "threshold": 0.95905315
    },
    "error": null
}
```

---

### 🛣️ 3. Búsqueda Filtrada (Street View)
Busca propiedades similares visualmente, pero restringiendo los resultados en la base de datos estrictamente a las etiquetas indicadas. Ideal para comparativas de fachadas específicas.

* **Método:** `POST`
* **Ruta:** `/search/filtered`
* **Formato:** `multipart/form-data`

| Campo | Tipo | Descripción |
| :--- | :--- | :--- |
| `file` | `File` | La imagen base tomada por el usuario. |
| `labels` | `String[]` | **[Opcional]** Filtro de etiquetas. Por defecto: `["frente", "frente 45 izquierda", "frente 45 derecha"]`. |


#### ✅ Respuesta Exitosa (Data)

```json
{
    "success": true,
    "message": "Búsqueda filtrada completada con éxito",
    "data": {
        "matches": [
            {
                "parent_id": "123e4567-e89b-12d3-a456-426614174000",
                "images": [
                    {
                        "score": 1.0,
                        "label": "frente"
                    },
                    {
                        "score": 1.0,
                        "label": "frente"
                    },
                    {
                        "score": 0.80623734,
                        "label": "frente 45 izquierda"
                    },
                    {
                        "score": 0.80623734,
                        "label": "frente 45 izquierda"
                    }
                ]
            }
        ],
        "threshold": null
    },
    "error": null
}

```
---

### 💬 4. Búsqueda por Texto (Multimodal)
Permite realizar búsquedas semánticas escribiendo en lenguaje natural. El sistema traduce la consulta automáticamente para maximizar la precisión con el modelo CLIP.

* **Método:** `POST`
* **Ruta:** `/search/text`
* **Formato:** `multipart/form-data`

| Campo | Tipo | Descripción |
| :--- | :--- | :--- |
| `text` | `String` | Frase descriptiva (ej: *"fachada moderna con ladrillos a la vista"*). |


#### ✅ Respuesta Exitosa (Data)


```json
{
    "success": true,
    "message": "Busqueda para 'casa con porton oscuro' realizada con éxito",
    "data": {
        "matches": [
            {
                "parent_id": "123e4567-e89b-12d3-a456-426614174000",
                "images": [
                    {
                        "score": 0.2890824,
                        "label": "frente 45 izquierda"
                    },
                    {
                        "score": 0.2890824,
                        "label": "frente 45 izquierda"
                    }
                ]
            }
        ],
        "threshold": 0.28603229327314195
    },
    "error": null
}
```

---



### 🗑️ 5. Eliminación de Entidad (Borrado en Cascada)
Borra de forma permanente todas las imágenes y vectores asociados a un UUID específico en la base de datos de Qdrant.

* **Método:** `DELETE`
* **Ruta:** `/delete/{parent_id}`

| Parámetro | Tipo | Ubicación | Descripción |
| :--- | :--- | :--- | :--- |
| `parent_id` | `UUID` | Path | El identificador único de la propiedad a eliminar. |

#### ✅ Respuesta Exitosa

```json
{
    "success": true,
    "message": "Se eliminaron las imagenes asociadas a la entidad con UUID <parent_id>",
    "data": null,
    "error": null
}
```

### ✏️ 6. Actualización de Etiqueta
Permite actualizar la etiqueta asociada a un vector específico. Esta operación realiza un cambio en el `payload` del punto almacenado en Qdrant, manteniendo la integridad de la entidad a través del `parent_id`.

* **Método:** `PATCH`
* **Ruta:** `/update-label`
* **Formato:** `application/json`

| Campo | Tipo | Requerido | Descripción |
| :--- | :--- | :--- | :--- |
| `uuid` | `String` | Sí | El identificador único del vector (ID de la imagen). |
| `new_label` | `String` | Sí | La nueva etiqueta que se asignará al vector. |

#### 📥 Ejemplo de Request (JSON)
```json
{
    "uuid": "d6f1c21d-4aae-4f83-99f5-b1996d906ed7",
    "new_label": "frente renovado",
}
```
#### ✅ Respuesta Exitosa
```json
{
    "success": true,
    "message": "Etiqueta y parent_id actualizados para d6f1c21d-4aae-4f83-99f5-b1996d906ed7",
    "data": {
        "uuid": "d6f1c21d-4aae-4f83-99f5-b1996d906ed7",
        "label": "frente renovado",
        "parent_id": "123e4567-e89b-12d3-a456-426614174000"
    },
    "error": null
}
```

## 🚀 Pruebas con Postman

Para facilitar el testeo y la integración de los endpoints, se incluye una colección de **Postman** lista para usar, ubicada en la raíz del proyecto.

### 📦 Archivo de Colección
* **Ruta:** `./consultas_postman.json`

### 🛠️ Pasos para empezar:

1. **Importar:** Abre Postman y arrastra el archivo JSON de la colección a tu espacio de trabajo.

2. **colocar header de autenticacion:** en cada consulta, coloca en en el header x-api-key con el mismo valor que definiste en archivo .env 

3. **Peticiones listas:** La colección incluye ejemplos preconfigurados con cuerpos `multipart/form-data` para:
    * Ingesta de imágenes (con carga de archivos).
    * Búsqueda genérica y filtrada.
    * Búsqueda por texto.
    * Eliminación por UUID.