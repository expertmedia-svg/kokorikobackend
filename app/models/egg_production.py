from beanie import Document
from pydantic import Field
from typing import Optional
from datetime import datetime

class EggProduction(Document):
    flock_id: str
    farm_id: str
    user_id: str
    date: datetime
    oeufs_collectes: int = 0
    oeufs_casses: int = 0
    oeufs_vendus: int = 0
    oeufs_consommes: int = 0
    stock_restant: int = 0
    prix_vente_unitaire: Optional[float] = None
    revenu_jour: Optional[float] = None
    taux_ponte: Optional[float] = None  # calculé automatiquement
    observation: Optional[str] = None
    alerte_baisse: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "egg_productions"
