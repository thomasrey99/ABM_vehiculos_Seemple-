from typing import Any


def success_response(
    data: Any = None,
    message: str = "Operation successful",
):
    return {
        "success": True,
        "message": message,
        "data": data,
        "error": None,
    }


def error_response(
    message: str,
    error: str,
    data: Any = None,
):
    return {
        "success": False,
        "message": message,
        "data": data,
        "error": error,
    }