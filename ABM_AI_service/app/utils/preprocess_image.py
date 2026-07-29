from PIL import Image, ImageOps
import io

def preprocess_image(image_bytes: bytes, target_size=(224, 224)) -> Image.Image:
    """
    Toma una imagen cruda, repara su rotación EXIF, la convierte al formato de color RGB y la recorta/escala uniformemente al tamaño requerido por el modelo (por defecto 224x224).
    """
    img = Image.open(io.BytesIO(image_bytes))
    img = ImageOps.exif_transpose(img)
    img = img.convert("RGB")
    img = ImageOps.fit(
        img, 
        target_size,
        method=Image.Resampling.LANCZOS
    )

    return img