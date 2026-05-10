from fastapi import APIRouter, Depends
from app.models.other_models import Notification
from app.core.security import get_current_user

router = APIRouter()

@router.get("/")
async def get_notifications(limit: int = 50, current_user=Depends(get_current_user)):
    notifs = await Notification.find(
        Notification.user_id == str(current_user.id)
    ).sort("-created_at").limit(limit).to_list()
    return [{"id": str(n.id), **n.dict(exclude={"id", "revision_id"})} for n in notifs]

@router.get("/unread-count")
async def get_unread_count(current_user=Depends(get_current_user)):
    count = await Notification.find(
        Notification.user_id == str(current_user.id),
        Notification.lu == False
    ).count()
    return {"count": count}

@router.patch("/{notif_id}/read")
async def mark_read(notif_id: str, current_user=Depends(get_current_user)):
    notif = await Notification.get(notif_id)
    if notif and notif.user_id == str(current_user.id):
        notif.lu = True
        await notif.save()
    return {"message": "Notification lue"}

@router.patch("/read-all")
async def mark_all_read(current_user=Depends(get_current_user)):
    notifs = await Notification.find(
        Notification.user_id == str(current_user.id),
        Notification.lu == False
    ).to_list()
    for n in notifs:
        n.lu = True
        await n.save()
    return {"message": f"{len(notifs)} notifications marquées comme lues"}
