"""
modules/memory/context_builder.py - Layer 1: In-context memory
Xay dung memory ngan han cho phien hien tai
"""
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession
from models.incident import Incident, IncidentObservation


async def get_recent_incidents_for_prompt(
    db: AsyncSession, service: str = None, host: str = None, limit: int = 5
) -> list[dict]:
    """Lay 5 incident gan nhat cung service/host, format cho Gemini prompt"""
    from sqlalchemy import or_

    conditions = []
    if host:
        conditions.append(Incident.impacted_host == host)
    if service:
        conditions.append(Incident.impacted_service == service)

    if not conditions:
        return []

    stmt = (
        select(Incident)
        .where(or_(*conditions))
        .order_by(desc(Incident.created_at))
        .limit(limit)
    )
    result = await db.execute(stmt)
    incidents = result.scalars().all()

    formatted = []
    for inc in incidents:
        # Lay observation cuoi cung neu co
        obs_stmt = (
            select(IncidentObservation)
            .where(IncidentObservation.incident_id == inc.id)
            .order_by(desc(IncidentObservation.created_at))
            .limit(1)
        )
        obs_result = await db.execute(obs_stmt)
        obs = obs_result.scalar_one_or_none()

        formatted.append({
            "created_at": str(inc.created_at),
            "severity": inc.severity,
            "status": inc.status,
            "title": inc.title,
            "action_taken": obs.action_taken if obs else "none",
            "outcome": obs.actual_outcome if obs else inc.status,
        })

    return formatted
