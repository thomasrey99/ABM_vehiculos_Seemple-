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
from app.modules.vehicles.schemas.update_vehicle_image_label_request import (
    UpdateVehicleImageLabelRequest,
)
from app.modules.vehicles.schemas.update_vehicle_request import (
    UpdateVehicleRequest,
)
from app.modules.vehicles.schemas.vehicle_response import VehicleResponse
from app.modules.vehicles.schemas.vehicle_search_response import (
    MatchedImageResponse,
    VehicleSearchMatchResponse,
    VehicleSearchResponse,
)
from app.services.recognition.models.image_search_result import (
    ImageSearchResult,
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
                embedding_status=EmbeddingStatus.PENDIENTE,
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

        Cada imagen viaja junto con SUS PROPIOS `details` (relación 1-a-N
        imagen→detalles), tal como espera `metadata.images` en el /ingest
        del servicio de reconocimiento — ya no se manda una lista de
        details aplanada a nivel vehículo.
        """

        images_to_index: list[tuple[UploadFile, str, list[str]]] = []

        for image_request in request.images:
            upload_file = files_map[image_request.filename]

            label = IMAGE_LABEL_TO_RECOGNITION_LABEL.get(
                image_request.label,
                image_request.label.value,
            )

            image_details = [
                detail.detail_type.value for detail in image_request.details
            ]

            images_to_index.append((upload_file, label, image_details))

        try:
            embedding_ids = await self.recognition_service.index_images(
                vehicle_id=vehicle.id,
                license_plate=vehicle.license_plate,
                brand=vehicle.brand,
                model=vehicle.model,
                color=vehicle.color or "",
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
            vehicle_image.embedding_status = EmbeddingStatus.COMPLETADO
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

    async def update(
        self,
        vehicle_id: UUID,
        request: UpdateVehicleRequest,
    ) -> VehicleResponse:
        """
        Actualiza parcialmente un vehículo. Si cambian brand/model/color/
        license_plate, esos campos también se replican en el servicio de
        reconocimiento (best effort: si falla, se loguea pero no se
        revierte la actualización ya persistida en nuestra base).
        """

        vehicle = await self.vehicle_repository.get_by_id(vehicle_id)

        if vehicle is None:
            raise NotFoundException("Vehículo no encontrado.")

        update_data = request.model_dump(exclude_unset=True)

        if not update_data:
            raise BadRequestException(
                "Debe enviarse al menos un campo para actualizar."
            )

        recognition_fields: dict[str, str] = {}

        if update_data.get("license_plate") is not None:
            new_plate = update_data["license_plate"].upper().strip()

            if new_plate != vehicle.license_plate:
                existing = await self.vehicle_repository.get_by_license_plate(
                    new_plate
                )

                if existing and existing.id != vehicle.id:
                    raise ConflictException(
                        "Ya existe un vehículo con esa patente."
                    )

                vehicle.license_plate = new_plate
                recognition_fields["license_plate"] = new_plate

        if update_data.get("brand") is not None:
            vehicle.brand = update_data["brand"].strip()
            recognition_fields["brand"] = vehicle.brand

        if update_data.get("model") is not None:
            vehicle.model = update_data["model"].strip()
            recognition_fields["model"] = vehicle.model

        if "color" in update_data:
            vehicle.color = (
                update_data["color"].strip() if update_data["color"] else None
            )
            if vehicle.color is not None:
                recognition_fields["color"] = vehicle.color

        if "year" in update_data:
            vehicle.year = update_data["year"]

        if "insurance_policy" in update_data:
            vehicle.insurance_policy = (
                update_data["insurance_policy"].strip()
                if update_data["insurance_policy"]
                else None
            )

        if "observations" in update_data:
            vehicle.observations = (
                update_data["observations"].strip()
                if update_data["observations"]
                else None
            )

        if update_data.get("is_active") is not None:
            vehicle.is_active = update_data["is_active"]

        try:
            await self.vehicle_repository.update(vehicle)
            await self.db.commit()
        except SQLAlchemyError as exc:
            await self.db.rollback()
            raise InternalServerException(
                "Error al actualizar el vehículo."
            ) from exc

        if recognition_fields:
            try:
                await self.recognition_service.update_vehicle_metadata(
                    vehicle_id=vehicle.id,
                    fields=recognition_fields,
                )
            except Exception:
                logger.exception(
                    "No fue posible actualizar los metadatos del "
                    "vehículo %s en el servicio de reconocimiento.",
                    vehicle.id,
                )

        vehicle = await self.vehicle_repository.get_by_id(vehicle_id)

        return VehicleResponse.model_validate(vehicle)

    async def update_image_label(
        self,
        vehicle_id: UUID,
        image_id: UUID,
        request: UpdateVehicleImageLabelRequest,
    ) -> VehicleResponse:
        """
        Actualiza el sector (label) de una imagen puntual. Si la imagen ya
        está indexada en el servicio de reconocimiento (tiene
        embedding_id), replica el cambio allá (best effort: si falla, se
        loguea pero el cambio local no se revierte).
        """

        image = await self.vehicle_repository.get_image_by_id(image_id)

        if image is None or image.vehicle_id != vehicle_id:
            raise NotFoundException("Imagen no encontrada.")

        image.label = request.label

        try:
            await self.db.commit()
        except SQLAlchemyError as exc:
            await self.db.rollback()
            raise InternalServerException(
                "Error al actualizar el label de la imagen."
            ) from exc

        if image.embedding_id:
            recognition_label = IMAGE_LABEL_TO_RECOGNITION_LABEL.get(
                request.label,
                request.label.value,
            )

            try:
                await self.recognition_service.update_label(
                    embedding_id=image.embedding_id,
                    new_label=recognition_label,
                )
            except Exception:
                logger.exception(
                    "No fue posible actualizar el label en el servicio "
                    "de reconocimiento para la imagen %s.",
                    image.id,
                )
        else:
            logger.info(
                "La imagen %s no tiene embedding_id (no está indexada "
                "en el servicio de reconocimiento); solo se actualizó "
                "el label localmente.",
                image.id,
            )

        vehicle = await self.vehicle_repository.get_by_id(vehicle_id)

        return VehicleResponse.model_validate(vehicle)

    async def replace_image(
        self,
        vehicle_id: UUID,
        image_id: UUID,
        file: UploadFile,
    ) -> VehicleResponse:
        """
        Reemplaza el archivo de una imagen puntual: sube el nuevo archivo
        a Cloud Storage, borra el anterior, y si la imagen ya estaba
        indexada en el servicio de reconocimiento, reemplaza también su
        embedding allá (best effort: si falla, se loguea pero el archivo
        ya quedó reemplazado localmente).
        """

        image = await self.vehicle_repository.get_image_by_id(image_id)

        if image is None or image.vehicle_id != vehicle_id:
            raise NotFoundException("Imagen no encontrada.")

        old_image_url = image.image_url

        uploaded_file = await self.storage_service.upload_file(
            file=file,
            destination=f"vehicles/{vehicle_id}",
        )

        image.filename = uploaded_file.filename
        image.image_url = uploaded_file.url

        try:
            await self.db.commit()
        except SQLAlchemyError as exc:
            await self.db.rollback()
            raise InternalServerException(
                "Error al actualizar la imagen del vehículo."
            ) from exc

        try:
            await self.storage_service.delete_file(old_image_url)
        except Exception:
            logger.exception(
                "No fue posible eliminar el archivo anterior de "
                "Cloud Storage para la imagen %s.",
                image.id,
            )

        if image.embedding_id:
            await file.seek(0)

            try:
                await self.recognition_service.replace_image(
                    embedding_id=image.embedding_id,
                    file=file,
                )
            except Exception:
                logger.exception(
                    "No fue posible reemplazar el embedding en el "
                    "servicio de reconocimiento para la imagen %s.",
                    image.id,
                )
        else:
            logger.info(
                "La imagen %s no tiene embedding_id (no está indexada "
                "en el servicio de reconocimiento); solo se reemplazó "
                "el archivo localmente.",
                image.id,
            )

        vehicle = await self.vehicle_repository.get_by_id(vehicle_id)

        return VehicleResponse.model_validate(vehicle)

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

    async def delete_image(
        self,
        vehicle_id: UUID,
        image_id: UUID,
    ) -> None:
        """
        Elimina una imagen puntual de un vehículo. Modo estricto, igual
        que el borrado de vehículo completo: primero se limpian los
        recursos externos (embedding en el servicio de reconocimiento e
        imagen en Cloud Storage); si cualquiera de los dos falla, se
        cancela la operación y la imagen NO se borra de la base.
        """

        image = await self.vehicle_repository.get_image_by_id(image_id)

        if image is None or image.vehicle_id != vehicle_id:
            raise NotFoundException("Imagen no encontrada.")

        if image.embedding_id:
            try:
                await self.recognition_service.delete_embedding(
                    image.embedding_id
                )
            except Exception as exc:
                logger.exception(
                    "No fue posible eliminar el embedding %s en el "
                    "servicio de reconocimiento. Se cancela la "
                    "eliminación de la imagen.",
                    image.embedding_id,
                )
                raise InternalServerException(
                    "No fue posible eliminar la imagen en el servicio "
                    "de reconocimiento."
                ) from exc

        try:
            await self.storage_service.delete_file(image.image_url)
        except Exception as exc:
            logger.exception(
                "No fue posible eliminar el archivo de Cloud Storage "
                "para la imagen %s. Se cancela la eliminación.",
                image.id,
            )
            raise InternalServerException(
                "No fue posible eliminar la imagen en Cloud Storage."
            ) from exc

        await self.vehicle_repository.delete_image(image)

        await self.db.commit()

    async def _build_search_response(
        self,
        result: ImageSearchResult,
    ) -> VehicleSearchResponse:

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
                            details=image.details or [],
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

        return await self._build_search_response(result)

    async def search_by_text(
        self,
        text: str,
    ) -> VehicleSearchResponse:
        """
        Busca vehículos mediante una consulta en lenguaje natural,
        delegando la búsqueda híbrida al servicio de reconocimiento
        y resolviendo cada vehicle_id devuelto contra nuestra base.
        """

        if not text or not text.strip():
            raise BadRequestException("El texto de búsqueda no puede estar vacío.")

        try:
            result = await self.recognition_service.search_by_text(text)
        except Exception as exc:
            logger.exception(
                "Falló la búsqueda por texto en el servicio de "
                "reconocimiento."
            )
            raise InternalServerException(
                "No fue posible completar la búsqueda por texto."
            ) from exc

        return await self._build_search_response(result)