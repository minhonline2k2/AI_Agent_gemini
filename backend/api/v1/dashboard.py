"""api/v1/dashboard.py - Thong ke tong hop"""
from datetime import datetime, timezone, timedelta
from fastapi import APIRouter, Depends
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_db
from models.incident import Incident
from models.agent import Agent
from models.rca import RCAResult
from modules.memory.pattern_analyzer import get_noisy_alerts, get_top_impacted_hosts, get_avg_confidence

router = APIRouter()


@router.get("/stats")
async def get_stats(db: AsyncSession = Depends(get_db)):
    # Dem incidents
    total = (await db.execute(select(func.count(Incident.id)))).scalar() or 0
    open_count = (await db.execute(
        select(func.count(Incident.id)).where(Incident.status.in_(["open", "acknowledged", "investigating"]))
    )).scalar() or 0
    critical = (await db.execute(
        select(func.count(Incident.id)).where(Incident.severity == "critical")
    )).scalar() or 0

    # Dem agents online
    agents_total = (await db.execute(select(func.count(Agent.id)))).scalar() or 0
    agents_online = (await db.execute(
        select(func.count(Agent.id)).where(Agent.status == "online")
    )).scalar() or 0

    # Overrides hom nay
    today = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0)
    overrides = (await db.execute(
        select(func.count(RCAResult.id)).where(RCAResult.override_applied == True).where(RCAResult.created_at >= today)
    )).scalar() or 0

    # Noisy alerts
    noisy = await get_noisy_alerts(db)
    top_hosts = await get_top_impacted_hosts(db)
    avg_conf = await get_avg_confidence(db)

    # Incidents by severity
    sev_result = await db.execute(
        select(Incident.severity, func.count(Incident.id)).group_by(Incident.severity)
    )
    by_severity = {r[0]: r[1] for r in sev_result.all()}

    return {
        "total_incidents": total,
        "open_incidents": open_count,
        "critical_incidents": critical,
        "agents_online": agents_online,
        "agents_total": agents_total,
        "avg_confidence": avg_conf,
        "overrides_today": overrides,
        "incidents_by_severity": by_severity,
        "noisy_alerts": noisy,
        "top_impacted_hosts": top_hosts,
    }
