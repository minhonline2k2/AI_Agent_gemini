"""
modules/audit/logger.py - Ghi nhat ky moi thao tac
Moi hanh dong trong he thong deu phai ghi audit trail
"""
import uuid
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from models.audit import AuditLog


async def audit_log(
    db: AsyncSession,
    event_type: str,
    actor: str,
    action: str,
    resource_type: str = None,
    resource_id=None,
    details: dict = None,
    actor_type: str = "system",
    ip_address: str = None,
):
    """
    Ghi 1 dong vao audit_logs

    Vi du su dung:
        await audit_log(db, "incident_created", "system", "create",
                       resource_type="incident", resource_id=inc.id)
    """
    log = AuditLog(
        id=uuid.uuid4(),
        event_type=event_type,
        actor=actor,
        actor_type=actor_type,
        action=action,
        resource_type=resource_type,
        resource_id=resource_id,
        details=details,
        ip_address=ip_address,
    )
    db.add(log)
    # Khong commit o day - de API router commit
    return log
