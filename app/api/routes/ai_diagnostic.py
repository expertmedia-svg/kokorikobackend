from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from pydantic import BaseModel
from typing import Optional, List
import base64

from app.models.ai_diagnostic import AIDiagnostic, InputType
from app.models.other_models import Notification
from app.services.ai_service import ask_ai
from app.core.security import get_current_user

router = APIRouter()

class DiagnosticRequest(BaseModel):
    question: str
    farm_id: Optional[str] = None
    flock_id: Optional[str] = None
    health_case_id: Optional[str] = None
    contexte: Optional[str] = None

@router.post("/diagnostic")
async def ai_diagnostic(data: DiagnosticRequest, current_user=Depends(get_current_user)):
    """Diagnostic IA par texte."""
    result = await ask_ai(data.question, context=data.contexte)
    
    diagnostic = AIDiagnostic(
        user_id=str(current_user.id),
        farm_id=data.farm_id,
        flock_id=data.flock_id,
        health_case_id=data.health_case_id,
        type_input=InputType.texte,
        question_utilisateur=data.question,
        reponse_ia=result["reponse"],
        diagnostic_probable=result.get("diagnostic_probable"),
        niveau_gravite=result.get("niveau_gravite"),
        causes_possibles=result.get("causes_possibles", []),
        actions_immediates=result.get("actions_immediates", []),
        conseils_biosecurite=result.get("conseils_biosecurite", []),
        traitement_propose=result.get("traitement_propose"),
        recommande_veterinaire=result.get("recommande_veterinaire", False),
        ai_provider=result.get("provider", "openai"),
        tokens_utilises=result.get("tokens", 0)
    )
    await diagnostic.insert()
    
    # Alerte si urgent
    if result.get("niveau_gravite") == "urgent":
        notif = Notification(
            user_id=str(current_user.id),
            titre="🚨 Situation urgente détectée par l'IA",
            message="L'IA a détecté une situation urgente. Contactez immédiatement un vétérinaire.",
            type="alerte_sante"
        )
        await notif.insert()
    
    return {
        "id": str(diagnostic.id),
        "reponse": result["reponse"],
        "diagnostic_probable": result.get("diagnostic_probable"),
        "niveau_gravite": result.get("niveau_gravite"),
        "causes_possibles": result.get("causes_possibles", []),
        "actions_immediates": result.get("actions_immediates", []),
        "conseils_biosecurite": result.get("conseils_biosecurite", []),
        "traitement_propose": result.get("traitement_propose"),
        "recommande_veterinaire": result.get("recommande_veterinaire", False),
        "provider": result.get("provider")
    }

@router.post("/diagnostic/photo")
async def ai_diagnostic_photo(
    question: str = Form(...),
    farm_id: Optional[str] = Form(None),
    flock_id: Optional[str] = Form(None),
    photos: List[UploadFile] = File([]),
    current_user=Depends(get_current_user)
):
    """Diagnostic IA avec photos."""
    images_b64 = []
    for photo in photos:
        content = await photo.read()
        images_b64.append(base64.b64encode(content).decode())
    
    result = await ask_ai(question, images_base64=images_b64 if images_b64 else None)
    
    diagnostic = AIDiagnostic(
        user_id=str(current_user.id),
        farm_id=farm_id,
        flock_id=flock_id,
        type_input=InputType.photo if images_b64 else InputType.texte,
        question_utilisateur=question,
        reponse_ia=result["reponse"],
        diagnostic_probable=result.get("diagnostic_probable"),
        niveau_gravite=result.get("niveau_gravite"),
        causes_possibles=result.get("causes_possibles", []),
        actions_immediates=result.get("actions_immediates", []),
        conseils_biosecurite=result.get("conseils_biosecurite", []),
        traitement_propose=result.get("traitement_propose"),
        recommande_veterinaire=result.get("recommande_veterinaire", False),
        ai_provider=result.get("provider", "openai"),
        tokens_utilises=result.get("tokens", 0)
    )
    await diagnostic.insert()
    
    return {
        "id": str(diagnostic.id),
        "reponse": result["reponse"],
        "niveau_gravite": result.get("niveau_gravite"),
        "recommande_veterinaire": result.get("recommande_veterinaire", False),
        **{k: v for k, v in result.items() if k not in ["reponse", "tokens", "provider"]}
    }

@router.get("/history")
async def get_diagnostic_history(limit: int = 20, current_user=Depends(get_current_user)):
    diagnostics = await AIDiagnostic.find(
        AIDiagnostic.user_id == str(current_user.id)
    ).sort("-created_at").limit(limit).to_list()
    
    return [{"id": str(d.id), **d.dict(exclude={"id", "revision_id"})} for d in diagnostics]

@router.get("/quick-tips")
async def get_quick_tips(current_user=Depends(get_current_user)):
    """Conseils rapides du jour."""
    tips = [
        {"emoji": "💧", "conseil": "Vérifiez que l'eau est propre et fraîche ce matin"},
        {"emoji": "🌡️", "conseil": "La température idéale du poulailler est entre 18°C et 24°C"},
        {"emoji": "🥚", "conseil": "Collectez les œufs 2 fois par jour pour éviter la casse"},
        {"emoji": "🧹", "conseil": "Nettoyez les mangeoires tous les 3 jours"},
        {"emoji": "👁️", "conseil": "Observez les poules qui mangent moins ou restent isolées"},
        {"emoji": "💊", "conseil": "Notez tout changement de comportement de vos poules"},
    ]
    return tips
