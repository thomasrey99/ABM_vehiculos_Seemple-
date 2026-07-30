from app.enums.image_label import ImageLabel


IMAGE_LABEL_TO_RECOGNITION_LABEL: dict[ImageLabel, str] = {
    ImageLabel.FRENTE: "frente",
    ImageLabel.FRENTE_IZQUIERDA: "frente 45 izquierda",
    ImageLabel.FRENTE_DERECHA: "frente 45 derecha",
    ImageLabel.LATERAL_IZQUIERDA: "lateral izquierda",
    ImageLabel.LATERAL_DERECHA: "lateral derecha",
    ImageLabel.ATRAS: "atras",
    ImageLabel.ATRAS_IZQUIERDA: "atras 45 izquierda",
    ImageLabel.ATRAS_DERECHA: "atras 45 derecha",
    ImageLabel.OTRO: "otro",
}