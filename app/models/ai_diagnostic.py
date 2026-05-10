from beanie import Document
from pydantic import Field
from typing import Optional, List
from datetime import datetime
from enum import Enum

class InputType(str, Enum):
    texte = "texte"
    audio = "audio"
    photo = "photo"
    mixte = "mixte"

class AIDiagnostic(Document):
    user_id: str
    farm_id: Optional[str] = None
    flock_id: Optional[str] = None
    health_case_id: Optional[str] = None
    type_input: InputType = InputType.texte
    question_utilisateur: str
    photos: List[str] = []
    reponse_ia: str
    diagnostic_probable: Optional[str] = None
    niveau_gravite: Optional[str] = None  # faible, moyen, urgent
    causes_possibles: Optional[List[str]] = []
    actions_immediates: Optional[List[str]] = []
    conseils_biosecurite: Optional[List[str]] = []
    traitement_propose: Optional[str] = None
    recommande_veterinaire: bool = False
    ai_provider: str = "openai"  # openai ou gemini
    tokens_utilises: Optional[int] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "ai_diagnostics"
