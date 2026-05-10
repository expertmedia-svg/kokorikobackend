from fastapi import APIRouter, Depends
from app.models.user import User
from app.models.farm import Farm
from app.models.health_case import HealthCase
from app.models.ai_diagnostic import AIDiagnostic
from app.models.other_models import DiseaseKnowledge
from app.core.security import require_admin
from pydantic import BaseModel
from typing import Optional, List

router = APIRouter()

class DiseaseCreate(BaseModel):
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

@router.get("/stats")
async def get_global_stats(admin=Depends(require_admin)):
    total_users = await User.count()
    total_farms = await Farm.count()
    total_health_cases = await HealthCase.count()
    total_diagnostics = await AIDiagnostic.count()
    urgent_cases = await HealthCase.find(HealthCase.resolu == False).count()
    
    return {
        "total_eleveurs": total_users,
        "total_elevages": total_farms,
        "total_cas_sante": total_health_cases,
        "cas_urgents_actifs": urgent_cases,
        "total_diagnostics_ia": total_diagnostics
    }

@router.get("/users")
async def list_users(skip: int = 0, limit: int = 50, admin=Depends(require_admin)):
    users = await User.find().skip(skip).limit(limit).to_list()
    return [{"id": str(u.id), "nom": u.nom, "prenom": u.prenom, "email": u.email,
             "telephone": u.telephone, "pays": u.pays, "role": u.role,
             "created_at": u.created_at} for u in users]

@router.get("/health-alerts")
async def get_health_alerts(admin=Depends(require_admin)):
    cases = await HealthCase.find(HealthCase.resolu == False).sort("-date").limit(100).to_list()
    return [{"id": str(c.id), **c.dict(exclude={"id", "revision_id"})} for c in cases]

@router.get("/ai-diagnostics")
async def get_ai_diagnostics(limit: int = 50, admin=Depends(require_admin)):
    diagnostics = await AIDiagnostic.find().sort("-created_at").limit(limit).to_list()
    return [{"id": str(d.id), **d.dict(exclude={"id", "revision_id"})} for d in diagnostics]

@router.get("/diseases")
async def get_diseases(admin=Depends(require_admin)):
    diseases = await DiseaseKnowledge.find().to_list()
    return [{"id": str(d.id), **d.dict(exclude={"id", "revision_id"})} for d in diseases]

@router.post("/diseases")
async def add_disease(data: DiseaseCreate, admin=Depends(require_admin)):
    disease = DiseaseKnowledge(**data.dict())
    await disease.insert()
    return {"id": str(disease.id), "message": "Maladie ajoutée à la base de connaissances"}

@router.patch("/users/{user_id}/toggle")
async def toggle_user(user_id: str, admin=Depends(require_admin)):
    user = await User.get(user_id)
    if not user:
        from fastapi import HTTPException
        raise HTTPException(404, "Utilisateur introuvable")
    user.is_active = not user.is_active
    await user.save()
    return {"message": f"Utilisateur {'activé' if user.is_active else 'désactivé'}"}
