from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from enum import Enum

from app.models.flock import Flock, FlockStatus
from app.core.security import get_current_user

router = APIRouter()

class FlockCreate(BaseModel):
    farm_id: str
    nom: str
    race: str = "Pondeuse locale"
    nombre_poules: int
    age_semaines: int = 0
    date_arrivee: datetime
    fournisseur: Optional[str] = None
    statut: FlockStatus = FlockStatus.actif
    prix_achat_unitaire: Optional[float] = None
    notes: Optional[str] = None

@router.get("/")
async def get_flocks(farm_id: Optional[str] = None, current_user=Depends(get_current_user)):
    query = Flock.find(Flock.user_id == str(current_user.id))
    if farm_id:
        query = Flock.find(Flock.user_id == str(current_user.id), Flock.farm_id == farm_id)
    flocks = await query.to_list()
    return [{"id": str(f.id), **f.dict(exclude={"id", "revision_id"})} for f in flocks]

@router.post("/")
async def create_flock(data: FlockCreate, current_user=Depends(get_current_user)):
    flock = Flock(**data.dict(), user_id=str(current_user.id))
    await flock.insert()
    return {"id": str(flock.id), "message": "Lot créé avec succès"}

@router.get("/{flock_id}")
async def get_flock(flock_id: str, current_user=Depends(get_current_user)):
    flock = await Flock.get(flock_id)
    if not flock or flock.user_id != str(current_user.id):
        raise HTTPException(404, "Lot introuvable")
    return {"id": str(flock.id), **flock.dict(exclude={"id", "revision_id"})}

@router.put("/{flock_id}")
async def update_flock(flock_id: str, data: FlockCreate, current_user=Depends(get_current_user)):
    flock = await Flock.get(flock_id)
    if not flock or flock.user_id != str(current_user.id):
        raise HTTPException(404, "Lot introuvable")
    for key, value in data.dict().items():
        setattr(flock, key, value)
    flock.updated_at = datetime.utcnow()
    await flock.save()
    return {"message": "Lot mis à jour"}

@router.patch("/{flock_id}/status")
async def update_flock_status(flock_id: str, statut: FlockStatus, current_user=Depends(get_current_user)):
    flock = await Flock.get(flock_id)
    if not flock or flock.user_id != str(current_user.id):
        raise HTTPException(404, "Lot introuvable")
    flock.statut = statut
    flock.updated_at = datetime.utcnow()
    await flock.save()
    return {"message": f"Statut mis à jour: {statut}"}

@router.delete("/{flock_id}")
async def delete_flock(flock_id: str, current_user=Depends(get_current_user)):
    flock = await Flock.get(flock_id)
    if not flock or flock.user_id != str(current_user.id):
        raise HTTPException(404, "Lot introuvable")
    await flock.delete()
    return {"message": "Lot supprimé"}
