from app.exceptions.app_exceptions import NotFoundException


class VehicleNotFoundException(NotFoundException):
    def __init__(self):
        super().__init__(
            message="Vehículo no encontrado.",
            error="VEHICLE_NOT_FOUND",
        )