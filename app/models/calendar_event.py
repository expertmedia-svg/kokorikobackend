from beanie import Document
from pydantic import Field
from typing import Optional
from datetime import datetime
from enum import Enum

class EventType(str, Enum):
    vaccination = "vaccination"
    nettoyage = "nettoyage"
    desinfection = "desinfection"
    temperature = "temperature"
    eau = "eau"
    alimentation = "alimentation"
    vermifugation = "vermifugation"
    ponte = "ponte"
    veterinaire = "veterinaire"
    autre = "autre"

class CalendarEvent(Document):
    user_id: str
    farm_id: Optional[str] = None
    flock_id: Optional[str] = None
    titre: str
    type_evenement: EventType
    date_prevue: datetime
    date_realisee: Optional[datetime] = None
    rappel_active: bool = True
    notes: Optional[str] = None
    realise: bool = False
    recurrence: Optional[str] = None  # "hebdomadaire", "mensuel", "annuel"
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "calendar_events"
