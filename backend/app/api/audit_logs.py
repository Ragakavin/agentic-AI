from typing import Optional
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.app.database.session import get_db
from backend.app.models.models import AuditLog
from backend.app.schemas.schemas import AuditLogOut

router = APIRouter(prefix="/audit-logs", tags=["Audit Trail"])

@router.get("", response_model=list[AuditLogOut])
def list_audit_logs(
    actor_type: Optional[str] = None,
    action: Optional[str] = None,
    search: Optional[str] = None,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    query = db.query(AuditLog)
    if actor_type:
        query = query.filter(AuditLog.actor_type == actor_type.upper())
    if action:
        query = query.filter(AuditLog.action.ilike(f"%{action}%"))
    if search:
        s = f"%{search}%"
        query = query.filter(
            (AuditLog.entity_id.ilike(s)) |
            (AuditLog.actor_name.ilike(s)) |
            (AuditLog.action.ilike(s))
        )
    return query.order_by(AuditLog.timestamp.desc()).limit(limit).all()
