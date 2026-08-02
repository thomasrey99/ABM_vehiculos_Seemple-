from abc import ABC, abstractmethod

from app.modules.vehicles.schemas.vehicle_filter_query import VehicleFilterQuery


class FilterExtractionService(ABC):

    @abstractmethod
    async def extract_filters(self, text: str) -> VehicleFilterQuery:
        """
        Analiza un texto en lenguaje natural (ej. "traeme todos los
        toyota corolla color blanco con choque atrás") y extrae los
        filtros estructurados de búsqueda que pudo identificar. Los
        campos no mencionados o no inferibles con confianza quedan en
        None. Nunca inventa valores no sugeridos por el texto.
        """
        ...