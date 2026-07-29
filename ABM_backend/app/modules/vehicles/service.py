from datetime import datetime, timezone
from uuid import UUID, uuid4

from fastapi import UploadFile
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging import logger
from app.enums.embedding_status import EmbeddingStatus
from app.exceptions.app_exceptions import (
    BadRequestException,
    ConflictException,
    InternalServerException,
    NotFoundException,
)
from app.mappings.image_label_mapping import IMAGE_LABEL_TO_RECOGNITION_LABEL
from app.models.image_detail import ImageDetail
from app.models.vehicle import Vehicle
from app.models.vehicle_image import VehicleImage
from app.modules.vehicles.repository import VehicleRepository
from app.modules.vehicles.schemas.create_vehicle_request import (
    CreateImageDetailRequest,
    CreateVehicleRequest,
)
from app.modules.vehicles.schemas.vehicle_response import VehicleResponse
from app.modules.vehicles.schemas.vehicle_search_response import (
    MatchedImageResponse,
    VehicleSearchMatchResponse,
    VehicleSearchResponse,
)
from app.services.recognition.recognition_service import RecognitionService
from app.services.storage.storage_service import StorageService


class VehicleService:
    def __init__(
        self,
        db: AsyncSession,
        vehicle_repository: VehicleRepository,
        storage_service: StorageService,
        recognition_service: RecognitionService,
    ):
        self.db = db
        self.vehicle_repository = vehicle_repository
        self.storage_service = storage_service
        self.recognition_service = recognition_service

    async def create(
        self,
        request: CreateVehicleRequest,
        files: list[UploadFile],
    ) -> VehicleResponse:

        if not request.images:
            raise BadRequestException("Debe enviarse al menos una imagen.")

        await self._validate_license_plate(request.license_plate)

        files_map = self._map_files(files)

        self._validate_files(
            request=request,
            files_map=files_map,
        )

        vehicle = self._build_vehicle(request)

        images = await self._build_images(
            vehicle=vehicle,
            request=request,
            files_map=files_map,
        )
        vehicle.images = images

        try:
            await self.vehicle_repository.create(vehicle)

            await self.db.commit()

        except SQLAlchemyError as exc:
            await self.db.rollback()

            raise InternalServerException("Error al guardar el vehículo.") from exc

        # A partir de acá el vehículo ya está persistido. La indexación en el
        # servicio de reconocimiento es "best effort": si falla, las imágenes
        # quedan con embedding_status=PENDING para reintentarse después, pero
        # no se aborta la creación del vehículo.
        #
        # Usamos la lista `images` capturada acá en vez de `vehicle.images`:
        # el refresh() dentro de vehicle_repository.create() expira la
        # relación `images` del objeto `vehicle`, y volver a leer
        # `vehicle.images` después dispara un lazy-load que, en modo async,
        # revienta con MissingGreenlet si no se hace dentro de un await
        # explícito. Usando la lista propia evitamos tocar esa relación.
        #
        # Pasamos el objeto `vehicle` (no solo su id) porque ahora también
        # necesitamos brand/model/color para el /ingest. Acceder a esos
        # atributos escalares es seguro (a diferencia de `vehicle.images`):
        # refresh() recarga inmediatamente las columnas propias del objeto,
        # solo expira relaciones — el problema de MissingGreenlet era
        # específico de la relación `images`, no de columnas simples.
        await self._index_vehicle_images(
            vehicle=vehicle,
            images=images,
            request=request,
            files_map=files_map,
        )

        vehicle = await self.vehicle_repository.get_by_id(vehicle.id)

        if vehicle is None:
            raise InternalServerException(
                "No fue posible recuperar el vehículo creado."
            )

        return VehicleResponse.model_validate(vehicle)

    async def _validate_license_plate(
        self,
        license_plate: str,
    ) -> None:

        vehicle = await self.vehicle_repository.get_by_license_plate(
            license_plate.upper().strip()
        )

        if vehicle:
            raise ConflictException("Ya existe un vehículo con esa patente.")

    def _map_files(
        self,
        files: list[UploadFile],
    ) -> dict[str, UploadFile]:

        files_map: dict[str, UploadFile] = {}

        for file in files:
            if not file.filename:
                raise BadRequestException("Uno de los archivos no posee nombre.")

            files_map[file.filename] = file

        return files_map

    def _validate_files(
        self,
        request: CreateVehicleRequest,
        files_map: dict[str, UploadFile],
    ) -> None:

        request_files = {image.filename for image in request.images}

        uploaded_files = set(files_map.keys())

        if request_files != uploaded_files:
            missing = request_files - uploaded_files
            extra = uploaded_files - request_files

            errors: list[str] = []

            if missing:
                errors.append("Archivos faltantes: " + ", ".join(sorted(missing)))

            if extra:
                errors.append("Archivos no utilizados: " + ", ".join(sorted(extra)))

            raise BadRequestException(" | ".join(errors))

    def _build_vehicle(
        self,
        request: CreateVehicleRequest,
    ) -> Vehicle:

        return Vehicle(
            id=uuid4(),
            license_plate=request.license_plate.upper().strip(),
            brand=request.brand.strip(),
            model=request.model.strip(),
            color=request.color.strip() if request.color else None,
            year=request.year,
            insurance_policy=request.insurance_policy.strip() if request.insurance_policy else None,
            observations=request.observations.strip() if request.observations else None,
            is_active=True,
        )

    async def _build_images(
        self,
        vehicle: Vehicle,
        request: CreateVehicleRequest,
        files_map: dict[str, UploadFile],
    ) -> list[VehicleImage]:

        images: list[VehicleImage] = []
        files: list[UploadFile] = []
        labels: list[str] = []

        for image_request in request.images:
            upload_file = files_map.get(image_request.filename)

            if upload_file is None:
                raise BadRequestException(
                    f"No se recibió el archivo '{image_request.filename}'."
                )

            uploaded_file = await self.storage_service.upload_file(
                file=upload_file,
                destination=f"vehicles/{vehicle.id}",
            )

            await upload_file.seek(0)

            image = VehicleImage(
                filename=uploaded_file.filename,
                image_url=uploaded_file.url,
                label=image_request.label,
                embedding_status=EmbeddingStatus.PENDING,
                details=self._build_details(image_request.details),
            )

            images.append(image)
            files.append(upload_file)
            labels.append(image_request.label.value)

        return images

    def _build_details(
        self,
        details: list[CreateImageDetailRequest],
    ) -> list[ImageDetail]:

        return [
            ImageDetail(
                detail_type=detail.detail_type,
                description=detail.description,
            )
            for detail in details
        ]

    async def _index_vehicle_images(
        self,
        vehicle: Vehicle,
        images: list[VehicleImage],
        request: CreateVehicleRequest,
        files_map: dict[str, UploadFile],
    ) -> None:
        """
        Envía las imágenes al servicio de reconocimiento para su embebido
        e indexado en Qdrant. Best effort: cualquier falla se loguea y las
        imágenes quedan con embedding_status=PENDING (valor por defecto)
        para ser reintentadas más adelante por un proceso aparte.

        Recibe `images` (la lista de VehicleImage que nosotros construimos
        en memoria) en vez de leerla desde `vehicle.images`, porque esa
        relación queda expirada tras el refresh() del repositorio y
        volver a accederla dispara un lazy-load que rompe en modo async
        (MissingGreenlet) si no se hace dentro de un await explícito.
        Los atributos escalares de `vehicle` (brand, model, color, id) sí
        son seguros de leer en este punto.
        """

        images_to_index: list[tuple[UploadFile, str]] = []
        all_details: list[str] = []

        for image_request in request.images:
            upload_file = files_map[image_request.filename]

            label = IMAGE_LABEL_TO_RECOGNITION_LABEL.get(
                image_request.label,
                image_request.label.value,
            )

            images_to_index.append((upload_file, label))

            all_details.extend(
                detail.detail_type.value for detail in image_request.details
            )

        try:
            embedding_ids = await self.recognition_service.index_images(
                vehicle_id=vehicle.id,
                license_plate=vehicle.license_plate,
                brand=vehicle.brand,
                model=vehicle.model,
                color=vehicle.color or "",
                details=all_details,
                images=images_to_index,
            )
        except Exception:
            logger.exception(
                "Falló la indexación en el servicio de reconocimiento "
                "para el vehículo %s. Las imágenes quedan con "
                "embedding_status=PENDING.",
                vehicle.id,
            )
            return

        now = datetime.now(timezone.utc)
        updated = False

        for vehicle_image, embedding_id in zip(images, embedding_ids):
            if embedding_id is None:
                continue

            vehicle_image.embedding_id = embedding_id
            vehicle_image.indexed_at = now
            vehicle_image.embedding_status = EmbeddingStatus.COMPLETED
            updated = True

        if not updated:
            return

        try:
            await self.db.commit()
        except SQLAlchemyError:
            await self.db.rollback()

            logger.exception(
                "No fue posible guardar el resultado de la indexación "
                "para el vehículo %s.",
                vehicle.id,
            )

    async def get_by_id(
        self,
        vehicle_id: UUID,
    ) -> VehicleResponse:

        vehicle = await self.vehicle_repository.get_by_id(vehicle_id)

        if vehicle is None:
            raise NotFoundException("Vehículo no encontrado.")

        return VehicleResponse.model_validate(vehicle)

    async def get_by_license_plate(
        self,
        license_plate: str,
    ) -> VehicleResponse:

        vehicle = await self.vehicle_repository.get_by_license_plate(
            license_plate.upper().strip()
        )

        if vehicle is None:
            raise NotFoundException("Vehículo no encontrado.")

        return VehicleResponse.model_validate(vehicle)

    async def get_all(
        self,
    ) -> list[VehicleResponse]:

        vehicles = await self.vehicle_repository.get_all()

        return [VehicleResponse.model_validate(vehicle) for vehicle in vehicles]

    async def delete(
        self,
        vehicle_id: UUID,
    ) -> None:
        """
        Elimina un vehículo. Modo estricto: primero se limpian los
        recursos externos (vectores en el servicio de reconocimiento e
        imágenes en Cloud Storage); si cualquiera de los dos falla, se
        cancela toda la operación y el vehículo NO se borra de la base.
        """

        vehicle = await self.vehicle_repository.get_by_id(vehicle_id)

        if vehicle is None:
            raise NotFoundException("Vehículo no encontrado.")

        try:
            await self.recognition_service.delete_by_id(vehicle_id)
        except Exception as exc:
            logger.exception(
                "No fue posible eliminar los embeddings del vehículo "
                "%s en el servicio de reconocimiento. Se cancela la "
                "eliminación.",
                vehicle_id,
            )
            raise InternalServerException(
                "No fue posible eliminar los datos del vehículo en el "
                "servicio de reconocimiento."
            ) from exc

        try:
            for image in vehicle.images:
                await self.storage_service.delete_file(image.image_url)
        except Exception as exc:
            logger.exception(
                "No fue posible eliminar las imágenes del vehículo %s "
                "en Cloud Storage. Se cancela la eliminación.",
                vehicle_id,
            )
            raise InternalServerException(
                "No fue posible eliminar las imágenes del vehículo en "
                "Cloud Storage."
            ) from exc

        await self.vehicle_repository.delete(vehicle)

        await self.db.commit()

    async def search_by_image(
        self,
        file: UploadFile,
    ) -> VehicleSearchResponse:
        """
        Busca vehículos visualmente similares a la imagen recibida,
        delegando la búsqueda vectorial al servicio de reconocimiento
        y resolviendo cada vehicle_id devuelto contra nuestra base.
        """

        try:
            result = await self.recognition_service.search_by_image(file)
        except Exception as exc:
            logger.exception(
                "Falló la búsqueda por imagen en el servicio de "
                "reconocimiento."
            )
            raise InternalServerException(
                "No fue posible completar la búsqueda por imagen."
            ) from exc

        matches: list[VehicleSearchMatchResponse] = []

        for match in result.matches:
            try:
                vehicle_id = UUID(match.vehicle_id)
            except (ValueError, TypeError):
                logger.warning(
                    "El servicio de reconocimiento devolvió un "
                    "vehicle_id inválido: %s",
                    match.vehicle_id,
                )
                continue

            vehicle = await self.vehicle_repository.get_by_id(vehicle_id)

            if vehicle is None:
                # El vector sigue indexado en Qdrant pero el vehículo ya
                # no existe en nuestra base (por ejemplo, fue eliminado).
                logger.warning(
                    "El servicio de reconocimiento encontró coincidencias "
                    "para un vehículo que ya no existe: %s",
                    vehicle_id,
                )
                continue

            if not match.images:
                continue

            best_score = max(image.score for image in match.images)

            matches.append(
                VehicleSearchMatchResponse(
                    vehicle=VehicleResponse.model_validate(vehicle),
                    score=best_score,
                    matched_images=[
                        MatchedImageResponse(
                            label=image.label,
                            score=image.score,
                        )
                        for image in match.images
                    ],
                )
            )

        # No reordenamos ni filtramos acá: el servicio de reconocimiento ya
        # aplica su propio umbral dinámico y devuelve los matches en el
        # orden de relevancia que corresponde.
        return VehicleSearchResponse(
            threshold=result.threshold,
            matches=matches,
        )