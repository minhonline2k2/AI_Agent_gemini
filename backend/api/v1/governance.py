"""api/v1/governance.py - Governance panel"""
from fastapi import APIRouter, Depends
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_db
from models.audit import AuditLog

router = APIRouter()


@router.get("")
async def get_governance(db: AsyncSession = Depends(get_db)):
    # AI auto actions
    stmt = (
        select(AuditLog)
        .where(AuditLog.actor_type.in_(["system", "agent"]))
        .order_by(desc(AuditLog.created_at))
        .limit(50)
    )
    result = await db.execute(stmt)
    auto_actions = result.scalars().all()

    # Overrides
    stmt2 = (
        select(AuditLog)
        .where(AuditLog.event_type == "rca_override")
        .order_by(desc(AuditLog.created_at))
        .limit(20)
    )
    result2 = await db.execute(stmt2)
    overrides = result2.scalars().all()

    return {
        "auto_actions": [
            {"id": str(a.id), "event_type": a.event_type, "action": a.action,
             "actor": a.actor, "resource_type": a.resource_type,
             "details": a.details, "created_at": str(a.created_at)}
            for a in auto_actions
        ],
        "overrides": [
            {"id": str(o.id), "event_type": o.event_type, "action": o.action,
             "details": o.details, "created_at": str(o.created_at)}
            for o in overrides
        ],
        "pending_approvals": [],  # Phase 5+
        "total_ai_actions": len(auto_actions),
        "total_overrides": len(overrides),
    }
