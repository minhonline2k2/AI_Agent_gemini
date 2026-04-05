"""
modules/ingestion/deduplicator.py - Kiem tra trung lap incident
Neu cung fingerprint va incident dang open -> khong tao moi
"""
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from models.incident import Incident


async def find_existing_incident(db: AsyncSession, fingerprint: str):
    """
    Tim incident dang open co cung fingerprint.
    Neu co -> tra ve incident do (de update thay vi tao moi)
    Neu khong -> tra ve None (tao incident moi)
    """
    stmt = (
        select(Incident)
        .where(Incident.fingerprint == fingerprint)
        .where(Incident.status.in_(["open", "acknowledged", "investigating"]))
        .order_by(Incident.created_at.desc())
        .limit(1)
    )
    result = await db.execute(stmt)
    return result.scalar_one_or_none()
