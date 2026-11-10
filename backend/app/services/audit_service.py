from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.audit_log import AuditLogModel

def record_audit_log(
    db: Session,
    case_id: str,
    action: str,
    new_status: str,
    previous_status: Optional[str] = None,
    actor: str = "SYSTEM",
    details: Optional[str] = None
) -> AuditLogModel:
    """Record an immutable audit log entry in the database."""
    log_entry = AuditLogModel(
        case_id=case_id,
        action=action,
        previous_status=previous_status,
        new_status=new_status,
        actor=actor,
        details=details
    )
    db.add(log_entry)
    db.commit()
    db.refresh(log_entry)
    return log_entry

def get_case_audit_trail(db: Session, case_id: str) -> List[AuditLogModel]:
    """Retrieve complete chronological audit history for a case."""
    return db.query(AuditLogModel).filter(
        AuditLogModel.case_id == case_id
    ).order_by(AuditLogModel.timestamp.asc()).all()

