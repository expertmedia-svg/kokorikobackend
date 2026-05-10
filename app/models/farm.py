from beanie import Document, Link
from pydantic import Field
from typing import Optional
from datetime import datetime
from bson import ObjectId

class Farm(Document):
    user_id: str
    nom: str
    localisation: Optional[str] = None
    village: Optional[str] = None
    pays: str = "Burkina Faso"
    capacite_totale: Optional[int] = None
    description: Optional[str] = None
    temperature_cible: float = 25.0  # °C idéal
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "farms"
