"""
modules/memory/pattern_analyzer.py - Layer 3: Pattern analysis
Phat hien alert lap lai, host bi anh huong nhieu
"""
from sqlalchemy import select, func, desc
from sqlalchemy.ext.asyncio import AsyncSession
from models.incident import Incident
from models.rca import RCAResult


async def get_noisy_alerts(db: AsyncSession, days: int = 30, limit: int = 10):
    """Top alert names xuat hien nhieu nhat trong N ngay"""
    from datetime import datetime, timezone, timedelta
    since = datetime.now(timezone.utc) - timedelta(days=days)
    stmt = (
        select(Incident.title, func.count(Incident.id).label("count"))
        .where(Incident.created_at >= since)
        .group_by(Incident.title)
        .order_by(desc("count"))
        .limit(limit)
    )
    result = await db.execute(stmt)
    return [{"title": r[0], "count": r[1]} for r in result.all()]


async def get_top_impacted_hosts(db: AsyncSession, limit: int = 10):
    """Top host bi incident nhieu nhat"""
    stmt = (
        select(Incident.impacted_host, func.count(Incident.id).label("count"))
        .where(Incident.impacted_host.isnot(None))
        .group_by(Incident.impacted_host)
        .order_by(desc("count"))
        .limit(limit)
    )
    result = await db.execute(stmt)
    return [{"host": r[0], "count": r[1]} for r in result.all()]


async def get_avg_confidence(db: AsyncSession):
    """Confidence trung binh cua AI"""
    stmt = select(func.avg(RCAResult.confidence))
    result = await db.execute(stmt)
    val = result.scalar()
    return round(val, 2) if val else 0.0
