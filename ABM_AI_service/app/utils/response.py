from typing import Any, Optional


def build_response(
    success: bool,
    data: Any = None,
    message: Optional[str] = None,
    error: Optional[str] = None,
):
    """
    Función estándar que unifica y construye el formato final de la respuesta JSON (éxito, datos, mensaje, error).
    """
    if success and not message:
        message = "Operation successful"

    if not success and not message:
        message = "Operation failed"

    return {"success": success, "data": data, "message": message, "error": error}
