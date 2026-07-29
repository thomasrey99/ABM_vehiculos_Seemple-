from app.enums.image_label import ImageLabel

# Basado en la taxonomía documentada por el servicio de reconocimiento.
# ⚠️ REAR_LEFT, REAR_RIGHT y OTHER no están en la taxonomía oficial:
# son un mapeo razonable propuesto, ajustar si el servicio espera otra cosa.
IMAGE_LABEL_TO_RECOGNITION_LABEL: dict[ImageLabel, str] = {
    ImageLabel.FRONT: "frente",
    ImageLabel.FRONT_LEFT: "frente 45 izquierda",
    ImageLabel.FRONT_RIGHT: "frente 45 derecha",
    ImageLabel.LEFT: "lateral izq",
    ImageLabel.RIGHT: "lateral der",
    ImageLabel.BACK: "atras",
    ImageLabel.REAR_LEFT: "atras 45 izquierda",
    ImageLabel.REAR_RIGHT: "atras 45 derecha",
    ImageLabel.OTHER: "otro",
}