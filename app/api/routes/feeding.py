from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, timedelta
from app.models.other_models import FeedingRecord, Notification
from app.core.security import get_current_user

router = APIRouter()
SEUIL_STOCK_FAIBLE_KG = 50

class FeedingCreate(BaseModel):
    flock_id: str
    farm_id: str
    date: datetime
    type_aliment: str
    quantite_kg: float
    stock_restant_kg: Optional[float] = None
    cout_fcfa: Optional[float] = None
    observation: Optional[str] = None

@router.post("/")
async def record_feeding(data: FeedingCreate, current_user=Depends(get_current_user)):
    alerte = data.stock_restant_kg is not None and data.stock_restant_kg < SEUIL_STOCK_FAIBLE_KG
    
    if alerte:
        notif = Notification(
            user_id=str(current_user.id),
            titre="⚠️ Stock aliment faible",
            message=f"Il ne reste que {data.stock_restant_kg} kg de {data.type_aliment}. Pensez à vous réapprovisionner.",
            type="info"
        )
        await notif.insert()
    
    record = FeedingRecord(**data.dict(), user_id=str(current_user.id), alerte_stock_faible=alerte)
    await record.insert()
    return {"id": str(record.id), "message": "Alimentation enregistrée", "alerte_stock_faible": alerte}

@router.get("/flock/{flock_id}")
async def get_feeding_records(flock_id: str, jours: int = 30, current_user=Depends(get_current_user)):
    depuis = datetime.utcnow() - timedelta(days=jours)
    records = await FeedingRecord.find(
        FeedingRecord.flock_id == flock_id,
        FeedingRecord.user_id == str(current_user.id),
        FeedingRecord.date >= depuis
    ).sort("-date").to_list()
    return [{"id": str(r.id), **r.dict(exclude={"id", "revision_id"})} for r in records]
