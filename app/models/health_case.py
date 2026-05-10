from beanie import Document
from pydantic import Field
from typing import Optional, List
from datetime import datetime
from enum import Enum

class GravityLevel(str, Enum):
    faible = "faible"
    moyen = "moyen"
    urgent = "urgent"

class HealthCase(Document):
    flock_id: str
    farm_id: str
    user_id: str
    date: datetime
    symptomes: List[str] = []
    description: Optional[str] = None
    photos: List[str] = []  # URLs des photos
    nombre_poules_touchees: int = 0
    mortalite: int = 0
    traitement_donne: Optional[str] = None
    veterinaire_contacte: bool = False
    nom_veterinaire: Optional[str] = None
    gravite: GravityLevel = GravityLevel.moyen
    diagnostic_ia: Optional[str] = None
    resolu: bool = False
    date_resolution: Optional[datetime] = None
    notes: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "health_cases"
