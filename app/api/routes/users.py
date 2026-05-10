from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional
from app.models.user import User, ExperienceLevel
from app.core.security import get_current_user

router = APIRouter()

class ProfileUpdate(BaseModel):
    nom: Optional[str] = None
    prenom: Optional[str] = None
    telephone: Optional[str] = None
    village: Optional[str] = None
    pays: Optional[str] = None
    langue: Optional[str] = None
    niveau_experience: Optional[ExperienceLevel] = None
    taille_elevage: Optional[int] = None

@router.get("/me")
async def get_profile(current_user=Depends(get_current_user)):
    return {
        "id": str(current_user.id),
        "nom": current_user.nom,
        "prenom": current_user.prenom,
        "email": current_user.email,
        "telephone": current_user.telephone,
        "role": current_user.role,
        "village": current_user.village,
        "pays": current_user.pays,
        "langue": current_user.langue,
        "niveau_experience": current_user.niveau_experience,
        "taille_elevage": current_user.taille_elevage
    }

@router.put("/me")
async def update_profile(data: ProfileUpdate, current_user=Depends(get_current_user)):
    for key, value in data.dict(exclude_none=True).items():
        setattr(current_user, key, value)
    await current_user.save()
    return {"message": "Profil mis à jour"}
