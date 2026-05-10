from beanie import Document
from pydantic import Field
from typing import Optional
from datetime import datetime, date
from enum import Enum

class FlockStatus(str, Enum):
    actif = "actif"
    malade = "malade"
    reforme = "reforme"
    vendu = "vendu"

class Flock(Document):
    farm_id: str
    user_id: str
    nom: str
    race: str = "Pondeuse locale"
    nombre_poules: int
    age_semaines: int = 0
    date_arrivee: datetime
    fournisseur: Optional[str] = None
    statut: FlockStatus = FlockStatus.actif
    prix_achat_unitaire: Optional[float] = None
    notes: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "flocks"
