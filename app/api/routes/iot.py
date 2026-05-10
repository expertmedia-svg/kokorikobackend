from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

from app.models.other_models import IoTReading, Notification
from app.core.security import get_current_user

router = APIRouter()

class TemperatureData(BaseModel):
    farm_id: str
    capteur_id: Optional[str] = None
    temperature: float
    timestamp: Optional[datetime] = None

class HumidityData(BaseModel):
    farm_id: str
    capteur_id: Optional[str] = None
    humidite: float
    timestamp: Optional[datetime] = None

class WaterData(BaseModel):
    farm_id: str
    capteur_id: Optional[str] = None
    consommation_eau_litres: float
    timestamp: Optional[datetime] = None

class IoTFullData(BaseModel):
    farm_id: str
    capteur_id: Optional[str] = None
    temperature: Optional[float] = None
    humidite: Optional[float] = None
    lumiere: Optional[float] = None
    ventilation: Optional[float] = None
    consommation_eau_litres: Optional[float] = None
    statut_capteur: str = "actif"

@router.post("/temperature")
async def post_temperature(data: TemperatureData, current_user=Depends(get_current_user)):
    """Reçoit les données de température depuis ESP32/Arduino."""
    alerte = None
    if data.temperature > 32:
        alerte = f"🌡️ ALERTE: Température trop élevée ({data.temperature}°C)"
    elif data.temperature < 15:
        alerte = f"🌡️ ALERTE: Température trop basse ({data.temperature}°C)"
    
    reading = IoTReading(
        farm_id=data.farm_id,
        user_id=str(current_user.id),
        capteur_id=data.capteur_id,
        temperature=data.temperature,
        timestamp=data.timestamp or datetime.utcnow(),
        alerte=alerte
    )
    await reading.insert()
    
    if alerte:
        notif = Notification(
            user_id=str(current_user.id),
            titre=alerte,
            message=f"Température détectée: {data.temperature}°C. Température idéale: 18-24°C",
            type="alerte_sante"
        )
        await notif.insert()
    
    return {"status": "ok", "temperature": data.temperature, "alerte": alerte}

@router.post("/humidity")
async def post_humidity(data: HumidityData, current_user=Depends(get_current_user)):
    """Reçoit les données d'humidité depuis ESP32/Arduino."""
    alerte = None
    if data.humidite > 75:
        alerte = f"💧 ALERTE: Humidité trop élevée ({data.humidite}%)"
    elif data.humidite < 40:
        alerte = f"💧 ALERTE: Humidité trop basse ({data.humidite}%)"
    
    reading = IoTReading(
        farm_id=data.farm_id,
        user_id=str(current_user.id),
        capteur_id=data.capteur_id,
        humidite=data.humidite,
        timestamp=data.timestamp or datetime.utcnow(),
        alerte=alerte
    )
    await reading.insert()
    return {"status": "ok", "humidite": data.humidite, "alerte": alerte}

@router.post("/water")
async def post_water(data: WaterData, current_user=Depends(get_current_user)):
    """Reçoit les données de consommation d'eau."""
    reading = IoTReading(
        farm_id=data.farm_id,
        user_id=str(current_user.id),
        capteur_id=data.capteur_id,
        consommation_eau_litres=data.consommation_eau_litres,
        timestamp=data.timestamp or datetime.utcnow()
    )
    await reading.insert()
    return {"status": "ok", "eau_litres": data.consommation_eau_litres}

@router.post("/data")
async def post_full_data(data: IoTFullData, current_user=Depends(get_current_user)):
    """Reçoit toutes les données IoT en une fois."""
    reading = IoTReading(
        **data.dict(),
        user_id=str(current_user.id),
        timestamp=datetime.utcnow()
    )
    await reading.insert()
    return {"status": "ok", "id": str(reading.id)}

@router.get("/status")
async def get_iot_status(farm_id: str, current_user=Depends(get_current_user)):
    """Retourne le dernier état connu des capteurs."""
    last_reading = await IoTReading.find(
        IoTReading.farm_id == farm_id,
        IoTReading.user_id == str(current_user.id)
    ).sort("-timestamp").limit(1).to_list()
    
    if not last_reading:
        return {
            "status": "aucun_capteur",
            "message": "Aucune donnée capteur disponible",
            "farm_id": farm_id
        }
    
    r = last_reading[0]
    return {
        "status": "actif",
        "derniere_lecture": r.timestamp.isoformat(),
        "temperature": r.temperature,
        "humidite": r.humidite,
        "lumiere": r.lumiere,
        "ventilation": r.ventilation,
        "eau_litres": r.consommation_eau_litres,
        "alerte": r.alerte
    }

@router.get("/history/{farm_id}")
async def get_iot_history(farm_id: str, limit: int = 48, current_user=Depends(get_current_user)):
    readings = await IoTReading.find(
        IoTReading.farm_id == farm_id,
        IoTReading.user_id == str(current_user.id)
    ).sort("-timestamp").limit(limit).to_list()
    
    return [{"id": str(r.id), **r.dict(exclude={"id", "revision_id"})} for r in readings]
