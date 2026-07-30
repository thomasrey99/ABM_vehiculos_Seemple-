from dataclasses import dataclass, field


@dataclass(slots=True)
class ImageMatchDetail:
    score: float
    label: str
    details: list[str] = field(default_factory=list)


@dataclass(slots=True)
class VehicleImageMatch:
    vehicle_id: str
    images: list[ImageMatchDetail] = field(default_factory=list)


@dataclass(slots=True)
class ImageSearchResult:
    matches: list[VehicleImageMatch]
    threshold: float | None