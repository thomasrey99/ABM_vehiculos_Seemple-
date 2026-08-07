"""
Tool: get_vehicle_images

Que hace:
  1. Llama al endpoint "get by id" de tu backend de vehiculos (abm-vehiculos-seemple).
  2. Extrae la(s) URL(es) de imagen que ese endpoint devuelve. En tu caso las imagenes
     se guardan en Google Cloud Storage y esas URLs ya son publicas/accesibles
     directamente desde el navegador (no requieren re-subida a otro storage).
  3. Devuelve esas URLs + el Markdown listo (![...](url)) para que el agente lo
     incluya literal en su respuesta.

Por que este approach:
  Orchestrate no aloja archivos ni renderiza base64/data URLs/iframe en el chat.
  Solo renderiza imagenes servidas desde una URL HTTPS accesible por el navegador
  del usuario. Como tus imagenes en GCS ya son publicas, no hace falta re-publicarlas
  en otro Object Storage: alcanza con devolver la URL de GCS tal cual.

  Si en algun momento el bucket de GCS pasa a ser privado (URLs firmadas de corta
  duracion o requieren credenciales), esta tool dejaria de funcionar tal cual y
  habria que agregar un paso de descarga + re-publicacion en un storage publico
  (o generar una signed URL de GCS con expiracion larga). Avisame si eso cambia.

Conexion necesaria (ya existente en tu instancia, reutilizada):

  app_id="vehicle_management_api_20260804084441828"
  Es la misma conexion "Vehicle Management API" que ya usan tus otras tools
  (Listar todos los vehiculos, Obtener un vehiculo por su ID, etc).

Import de la tool (CLI del ADK) -- SIN remap, usando el app_id real directo:

  orchestrate tools import -k python \
      -f get_vehicle_images_tool.py \
      -r requirements.txt \
      -a vehicle_management_api_20260804084441828

Testeo local (emulando la conexion):

  export WXO_SECURITY_SCHEMA_vehicle_management_api_20260804084441828=api_key_auth
  export WXO_CONNECTION_vehicle_management_api_20260804084441828_api_key=tu_api_key
"""

from typing import Dict, List

import requests
from ibm_watsonx_orchestrate.agent_builder.connections import ConnectionType
from ibm_watsonx_orchestrate.agent_builder.tools import tool
from ibm_watsonx_orchestrate.run import connections

BACKEND_APP_ID = "vehicle_management_api_20260804084441828"


def _get_backend_headers() -> Dict[str, str]:
    """Arma los headers de auth para el backend segun el tipo de conexion configurado."""
    connection_type = connections.connection_type(BACKEND_APP_ID)
    headers = {"Accept": "application/json"}

    if connection_type == ConnectionType.API_KEY_AUTH:
        creds = connections.api_key_auth(BACKEND_APP_ID)
        headers["x-api-key"] = creds.api_key
    elif connection_type == ConnectionType.BEARER_TOKEN:
        creds = connections.bearer_token(BACKEND_APP_ID)
        headers["Authorization"] = f"Bearer {creds.token}"
    elif connection_type == ConnectionType.BASIC_AUTH:
        creds = connections.basic_auth(BACKEND_APP_ID)
        headers["Authorization"] = requests.auth._basic_auth_str(
            creds.username, creds.password
        )
    else:
        raise ValueError(
            f"Tipo de conexion no soportado para {BACKEND_APP_ID}: {connection_type}"
        )

    return headers


def _extract_image_urls(vehicle: dict) -> List[str]:
    """Extrae URLs de imagen (GCS) de la respuesta del get-by-id.

    Ajustar esta funcion a la forma REAL de tu respuesta. Cubre los casos mas
    comunes: campo unico imageUrl/image_url, o listas images/imageUrls/photos
    con strings u objetos {"url": ...}.
    """
    urls: List[str] = []

    single = vehicle.get("imageUrl") or vehicle.get("image_url")
    if single:
        urls.append(single)

    for key in ("images", "imageUrls", "image_urls", "photos"):
        value = vehicle.get(key)
        if isinstance(value, list):
            for item in value:
                if isinstance(item, str):
                    urls.append(item)
                elif isinstance(item, dict) and item.get("url"):
                    urls.append(item["url"])

    return urls


@tool(
    name="get_vehicle_images",
    description=(
        "Obtiene un vehiculo por id desde el backend y devuelve las URLs publicas "
        "de sus imagenes (alojadas en Google Cloud Storage) junto con el Markdown "
        "listo para mostrarlas en el chat. Nunca devuelve base64 ni data URLs."
    ),
    expected_credentials=[
        {
            "app_id": BACKEND_APP_ID,
            "type": [
                ConnectionType.API_KEY_AUTH,
                ConnectionType.BEARER_TOKEN,
                ConnectionType.BASIC_AUTH,
            ],
        },
    ],
)
def get_vehicle_images(vehicle_id: str, backend_base_url: str) -> dict:
    """Obtiene las URLs publicas de imagen de un vehiculo (GCS).

    Args:
        vehicle_id (str): Id del vehiculo a consultar (get by id).
        backend_base_url (str): URL base del endpoint get-by-id del backend,
            ej. "https://mi-backend.com/api/vehiculos" (se le concatena /{vehicle_id}).

    Returns:
        dict: {
            "vehicle_id": str,
            "image_count": int,
            "public_image_urls": [str, ...],
            "images_markdown": str,  # una o mas lineas ![...](url) listas para el chat
        }
    """
    headers = _get_backend_headers()
    resp = requests.get(
        f"{backend_base_url.rstrip('/')}/{vehicle_id}", headers=headers, timeout=30
    )
    resp.raise_for_status()
    vehicle = resp.json()

    public_urls = _extract_image_urls(vehicle)

    markdown_lines = [
        f"![Imagen del vehiculo {vehicle_id}]({url})" for url in public_urls
    ]

    return {
        "vehicle_id": vehicle_id,
        "image_count": len(public_urls),
        "public_image_urls": public_urls,
        "images_markdown": "\n".join(markdown_lines),
    }