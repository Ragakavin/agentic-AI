from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.app.database.session import get_db
from backend.app.models.models import Notification
from backend.app.schemas.schemas import NotificationOut

router = APIRouter(prefix="/notifications", tags=["Notifications"])

@router.get("", response_model=list[NotificationOut])
def list_notifications(limit: int = 50, db: Session = Depends(get_db)):
    return db.query(Notification).order_by(Notification.created_at.desc()).limit(limit).all()

@router.get("/unread-count")
def get_unread_count(db: Session = Depends(get_db)):
    count = db.query(Notification).filter(Notification.is_read == False).count()
    return {"unread_count": count}

@router.post("/{id}/read")
def mark_notification_read(id: int, db: Session = Depends(get_db)):
    notif = db.query(Notification).filter(Notification.id == id).first()
    if not notif:
        raise HTTPException(status_code=404, detail="Notification not found")
    notif.is_read = True
    db.commit()
    return {"status": "SUCCESS"}

@router.post("/read-all")
def mark_all_read(db: Session = Depends(get_db)):
    db.query(Notification).update({Notification.is_read: True})
    db.commit()
    return {"status": "SUCCESS"}
