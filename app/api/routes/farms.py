from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

from app.models.farm import Farm
from app.core.security import get_current_user

router = APIRouter()

class FarmCreate(BaseModel):
    nom: str
    localisation: Optional[str] = None
    village: Optional[str] = None
    pays: str = "Burkina Faso"
    capacite_totale: Optional[int] = None
    description: Optional[str] = None
    temperature_cible: float = 25.0

@router.get("/")
async def get_farms(current_user=Depends(get_current_user)):
    farms = await Farm.find(Farm.user_id == str(current_user.id)).to_list()
    return [{"id": str(f.id), **f.dict(exclude={"id", "revision_id"})} for f in farms]

@router.post("/")
async def create_farm(data: FarmCreate, current_user=Depends(get_current_user)):
    farm = Farm(**data.dict(), user_id=str(current_user.id))
    await farm.insert()
    return {"id": str(farm.id), "message": "Élevage créé avec succès", **data.dict()}

@router.get("/{farm_id}")
async def get_farm(farm_id: str, current_user=Depends(get_current_user)):
    farm = await Farm.get(farm_id)
    if not farm or farm.user_id != str(current_user.id):
        raise HTTPException(404, "Élevage introuvable")
    return {"id": str(farm.id), **farm.dict(exclude={"id", "revision_id"})}

@router.put("/{farm_id}")
async def update_farm(farm_id: str, data: FarmCreate, current_user=Depends(get_current_user)):
    farm = await Farm.get(farm_id)
    if not farm or farm.user_id != str(current_user.id):
        raise HTTPException(404, "Élevage introuvable")
    
    for key, value in data.dict().items():
        setattr(farm, key, value)
    farm.updated_at = datetime.utcnow()
    await farm.save()
    return {"message": "Élevage mis à jour"}

@router.delete("/{farm_id}")
async def delete_farm(farm_id: str, current_user=Depends(get_current_user)):
    farm = await Farm.get(farm_id)
    if not farm or farm.user_id != str(current_user.id):
        raise HTTPException(404, "Élevage introuvable")
    await farm.delete()
    return {"message": "Élevage supprimé"}

@router.get("/{farm_id}/dashboard")
async def farm_dashboard(farm_id: str, current_user=Depends(get_current_user)):
    """Tableau de bord complet d'un élevage."""
    from app.models.flock import Flock, FlockStatus
    from app.models.egg_production import EggProduction
    from app.models.health_case import HealthCase
    from app.models.other_models import Expense, Sale, Notification
    from datetime import date, timedelta
    
    farm = await Farm.get(farm_id)
    if not farm or farm.user_id != str(current_user.id):
        raise HTTPException(404, "Élevage introuvable")
    
    # Lots actifs
    flocks = await Flock.find(
        Flock.farm_id == farm_id,
        Flock.statut == FlockStatus.actif
    ).to_list()
    
    total_poules = sum(f.nombre_poules for f in flocks)
    
    # Production du jour
    today = datetime.combine(date.today(), datetime.min.time())
    tomorrow = today + timedelta(days=1)
    
    productions_jour = await EggProduction.find(
        EggProduction.farm_id == farm_id,
        EggProduction.date >= today,
        EggProduction.date < tomorrow
    ).to_list()
    
    oeufs_jour = sum(p.oeufs_collectes for p in productions_jour)
    taux_ponte = (oeufs_jour / total_poules * 100) if total_poules > 0 else 0
    
    # Mortalité 7 derniers jours
    semaine_passee = today - timedelta(days=7)
    health_cases = await HealthCase.find(
        HealthCase.farm_id == farm_id,
        HealthCase.date >= semaine_passee
    ).to_list()
    mortalite_semaine = sum(h.mortalite for h in health_cases)
    alertes_actives = len([h for h in health_cases if not h.resolu])
    
    # Finances du mois
    debut_mois = today.replace(day=1)
    depenses = await Expense.find(
        Expense.farm_id == farm_id,
        Expense.date >= debut_mois
    ).to_list()
    ventes = await Sale.find(
        Sale.farm_id == farm_id,
        Sale.date >= debut_mois
    ).to_list()
    
    total_depenses = sum(d.montant_fcfa for d in depenses)
    total_revenus = sum(v.montant_total for v in ventes)
    benefice = total_revenus - total_depenses
    
    # Notifications non lues
    notifs = await Notification.find(
        Notification.user_id == str(current_user.id),
        Notification.lu == False
    ).to_list()
    
    return {
        "farm": {"id": farm_id, "nom": farm.nom},
        "total_poules": total_poules,
        "nombre_lots_actifs": len(flocks),
        "oeufs_jour": oeufs_jour,
        "taux_ponte": round(taux_ponte, 1),
        "mortalite_semaine": mortalite_semaine,
        "alertes_actives": alertes_actives,
        "finances_mois": {
            "depenses": total_depenses,
            "revenus": total_revenus,
            "benefice": benefice
        },
        "notifications_non_lues": len(notifs)
    }
