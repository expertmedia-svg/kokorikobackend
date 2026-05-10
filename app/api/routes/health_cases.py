"""
health_cases.py - Routes santé
"""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from app.models.health_case import HealthCase, GravityLevel
from app.core.security import get_current_user

router = APIRouter()

class HealthCaseCreate(BaseModel):
    flock_id: str
    farm_id: str
    date: str  # Accept ISO8601 string
    symptomes: List[str] = []
    description: Optional[str] = None
    nombre_poules_touchees: int = 0
    mortalite: int = 0
    traitement_donne: Optional[str] = None
    veterinaire_contacte: bool = False
    nom_veterinaire: Optional[str] = None
    gravite: GravityLevel = GravityLevel.moyen
    notes: Optional[str] = None

@router.get("/")
async def get_health_cases(farm_id: Optional[str] = None, current_user=Depends(get_current_user)):
    query_filters = [HealthCase.user_id == str(current_user.id)]
    if farm_id:
        query_filters.append(HealthCase.farm_id == farm_id)
    cases = await HealthCase.find(*query_filters).sort("-date").to_list()
    return [{"id": str(c.id), **c.dict(exclude={"id", "revision_id"})} for c in cases]

@router.post("/")
async def create_health_case(data: HealthCaseCreate, current_user=Depends(get_current_user)):
    # Parse datetime from ISO8601 string
    try:
        if isinstance(data.date, str):
            case_date = datetime.fromisoformat(data.date.replace('Z', '+00:00'))
        else:
            case_date = data.date
    except (ValueError, AttributeError):
        raise HTTPException(400, "Format date invalide. Utilisez ISO8601.")

    case = HealthCase(
        flock_id=data.flock_id,
        farm_id=data.farm_id,
        user_id=str(current_user.id),
        date=case_date,
        symptomes=data.symptomes,
        description=data.description,
        nombre_poules_touchees=data.nombre_poules_touchees,
        mortalite=data.mortalite,
        traitement_donne=data.traitement_donne,
        veterinaire_contacte=data.veterinaire_contacte,
        nom_veterinaire=data.nom_veterinaire,
        gravite=data.gravite,
        notes=data.notes
    )
    await case.insert()
    return {"id": str(case.id), "message": "Cas sanitaire enregistré"}

@router.put("/{case_id}/resolve")
async def resolve_health_case(case_id: str, current_user=Depends(get_current_user)):
    case = await HealthCase.get(case_id)
    if not case or case.user_id != str(current_user.id):
        raise HTTPException(404, "Cas introuvable")
    case.resolu = True
    case.date_resolution = datetime.utcnow()
    await case.save()
    return {"message": "Cas marqué comme résolu"}

@router.delete("/{case_id}")
async def delete_health_case(case_id: str, current_user=Depends(get_current_user)):
    case = await HealthCase.get(case_id)
    if not case or case.user_id != str(current_user.id):
        raise HTTPException(404, "Cas introuvable")
    await case.delete()
    return {"message": "Cas supprimé"}
