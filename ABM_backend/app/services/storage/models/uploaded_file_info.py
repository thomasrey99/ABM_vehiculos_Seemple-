from dataclasses import dataclass


@dataclass(slots=True)
class UploadedFileInfo:
    """
    Información del archivo almacenado.
    """

    filename: str

    url: str