from beanie import Document
from pydantic import Field
from typing import Optional, List
from datetime import datetime
from enum import Enum


class FeedingRecord(Document):
    flock_id: str
    farm_id: str
    user_id: str
    date: datetime
    type_aliment: str  # maïs, soja, aliment complet, etc.
    quantite_kg: float
    stock_restant_kg: Optional[float] = None
    cout_fcfa: Optional[float] = None
    alerte_stock_faible: bool = False
    observation: Optional[str] = None
    conseil_ia: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "feeding_records"


class IoTReading(Document):
    farm_id: str
    user_id: str
    capteur_id: Optional[str] = None
    temperature: Optional[float] = None  # °C
    humidite: Optional[float] = None     # %
    lumiere: Optional[float] = None      # lux
    ventilation: Optional[float] = None  # m/s
    consommation_eau_litres: Optional[float] = None
    statut_capteur: str = "actif"
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    alerte: Optional[str] = None

    class Settings:
        name = "iot_readings"


class ExpenseType(str, Enum):
    alimentation = "alimentation"
    medicament = "medicament"
    materiel = "materiel"
    main_oeuvre = "main_oeuvre"
    transport = "transport"
    eau_electricite = "eau_electricite"
    veterinaire = "veterinaire"
    achat_poules = "achat_poules"
    autre = "autre"

class Expense(Document):
    user_id: str
    farm_id: Optional[str] = None
    flock_id: Optional[str] = None
    type_depense: ExpenseType
    description: str
    montant_fcfa: float
    date: datetime
    fournisseur: Optional[str] = None
    note: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "expenses"


class Sale(Document):
    user_id: str
    farm_id: Optional[str] = None
    flock_id: Optional[str] = None
    type_vente: str  # "oeufs", "poules", "fumier"
    quantite: float
    prix_unitaire: float
    montant_total: float
    date: datetime
    acheteur: Optional[str] = None
    note: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "sales"


class Notification(Document):
    user_id: str
    titre: str
    message: str
    type: str  # "alerte_sante", "rappel", "info", "baisse_ponte"
    lu: bool = False
    data: Optional[dict] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "notifications"


class DiseaseKnowledge(Document):
    nom: str
    nom_local: Optional[str] = None
    symptomes: List[str] = []
    causes: List[str] = []
    traitement_general: Optional[str] = None
    prevention: Optional[str] = None
    gravite: str = "moyen"
    necessite_veterinaire: bool = True
    region_frequente: Optional[str] = None
    saison: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        name = "disease_knowledge_base"
