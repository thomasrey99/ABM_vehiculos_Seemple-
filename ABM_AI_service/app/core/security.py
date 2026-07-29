from fastapi import Security, HTTPException, status
from fastapi.security import APIKeyHeader
from app.config.settings import settings

API_KEY_NAME = "X-API-Key"

api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)


async def verify_api_key(api_key: str = Security(api_key_header)):
    """
    Revisa en cada petición que el header de seguridad de la API (X-API-Key) exista y coincida con el de las variables de entorno para evitar accesos no autorizados.
    """
    if not api_key or api_key != settings.SERVICE_API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Acceso denegado: API Key inválida o faltante",
        )
    return api_key
