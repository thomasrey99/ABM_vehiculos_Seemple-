from uuid import UUID

from pydantic import BaseModel, ConfigDict


class VehicleSummaryResponse(BaseModel):
    """
    Versión liviana de VehicleResponse, sin `images` ni el resto de los
    campos secundarios. Se usa en los endpoints que devuelven VARIOS
    vehículos a la vez (listado completo, búsqueda por filtros, búsqueda
    por imagen/texto) para no explotar el tamaño de la respuesta: cada
    vehículo puede traer múltiples imágenes con URLs y detalles, y eso
    multiplicado por N vehículos es lo que generaba payloads gigantes
    (y el error de `context_length_exceeded` del lado del agente de IA
    en watsonx Orchestrate).

    Los endpoints que devuelven UN solo vehículo (get_by_id,
    get_by_license_plate, create, update, update_image_label,
    replace_image) siguen usando VehicleResponse completo, con imágenes
    y detalles incluidos.
    """

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    license_plate: str
    brand: str
    model: str
    insurance_policy: str | None