from beanie import Document
from pydantic import EmailStr, Field
from typing import Optional
from datetime import datetime
from enum import Enum

class UserRole(str, Enum):
    eleveur = "eleveur"
    veterinaire = "veterinaire"
    admin = "admin"

class ExperienceLevel(str, Enum):
    debutant = "debutant"
    intermediaire = "intermediaire"
    expert = "expert"

class User(Document):
    nom: str
    prenom: str
    email: Optional[EmailStr] = None
    telephone: Optional[str] = None
    password_hash: str
    role: UserRole = UserRole.eleveur
    village: Optional[str] = None
    pays: str = "Burkina Faso"
    langue: str = "fr"
    niveau_experience: ExperienceLevel = ExperienceLevel.debutant
    taille_elevage: Optional[int] = None  # nombre de poules total
    photo_url: Optional[str] = None
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    last_login: Optional[datetime] = None

    class Settings:
        name = "users"
        
    class Config:
        json_schema_extra = {
            "example": {
                "nom": "Ouédraogo",
                "prenom": "Ibrahima",
                "email": "ibrahima@example.com",
                "telephone": "+22670000000",
                "role": "eleveur",
                "village": "Koudougou",
                "pays": "Burkina Faso"
            }
        }
