from dataclasses import dataclass


@dataclass(slots=True)
class DetectedDamage:
    detail_type: str
    description: str | None = None