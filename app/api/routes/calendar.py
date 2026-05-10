from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from app.models.calendar_event import CalendarEvent, EventType
from app.core.security import get_current_user

router = APIRouter()

class EventCreate(BaseModel):
    titre: str
    type_evenement: EventType
    date_prevue: datetime
    farm_id: Optional[str] = None
    flock_id: Optional[str] = None
    rappel_active: bool = True
    notes: Optional[str] = None
    recurrence: Optional[str] = None

@router.get("/")
async def get_events(current_user=Depends(get_current_user)):
    events = await CalendarEvent.find(
        CalendarEvent.user_id == str(current_user.id)
    ).sort("date_prevue").to_list()
    return [{"id": str(e.id), **e.dict(exclude={"id", "revision_id"})} for e in events]

@router.post("/")
async def create_event(data: EventCreate, current_user=Depends(get_current_user)):
    event = CalendarEvent(**data.dict(), user_id=str(current_user.id))
    await event.insert()
    return {"id": str(event.id), "message": "Événement créé"}

@router.patch("/{event_id}/done")
async def mark_done(event_id: str, current_user=Depends(get_current_user)):
    event = await CalendarEvent.get(event_id)
    if not event or event.user_id != str(current_user.id):
        raise HTTPException(404, "Événement introuvable")
    event.realise = True
    event.date_realisee = datetime.utcnow()
    await event.save()
    return {"message": "Événement marqué comme réalisé"}

@router.delete("/{event_id}")
async def delete_event(event_id: str, current_user=Depends(get_current_user)):
    event = await CalendarEvent.get(event_id)
    if not event or event.user_id != str(current_user.id):
        raise HTTPException(404, "Événement introuvable")
    await event.delete()
    return {"message": "Événement supprimé"}

@router.get("/upcoming")
async def get_upcoming(jours: int = 7, current_user=Depends(get_current_user)):
    from datetime import timedelta
    now = datetime.utcnow()
    limit_date = now + timedelta(days=jours)
    events = await CalendarEvent.find(
        CalendarEvent.user_id == str(current_user.id),
        CalendarEvent.date_prevue >= now,
        CalendarEvent.date_prevue <= limit_date,
        CalendarEvent.realise == False
    ).sort("date_prevue").to_list()
    return [{"id": str(e.id), **e.dict(exclude={"id", "revision_id"})} for e in events]
