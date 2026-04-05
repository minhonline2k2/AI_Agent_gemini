"""
modules/memory/operational_db.py - Layer 2: Operational DB memory
Truy van thong tin van hanh tu database
"""
from sqlalchemy import select, func, desc
from sqlalchemy.ext.asyncio import AsyncSession
from models.incident import Incident
from models.system_info import SystemInfo
from models.knowledge import KnowledgeBase


async def get_system_info_for_host(db: AsyncSession, hostname: str) -> dict:
    """Lay thong tin he thong cua 1 host"""
    stmt = select(SystemInfo).where(SystemInfo.hostname == hostname)
    result = await db.execute(stmt)
    info = result.scalar_one_or_none()
    if not info:
        return {}
    return {
        "hostname": info.hostname,
        "role": info.role,
        "criticality": info.criticality,
        "dependencies": info.dependencies,
        "notes": info.notes,
    }


async def get_related_known_issues(db: AsyncSession, service: str = None) -> list:
    """Lay known issues lien quan den service"""
    stmt = (
        select(KnowledgeBase)
        .where(KnowledgeBase.type == "known_issue")
        .where(KnowledgeBase.status == "active")
        .limit(5)
    )
    result = await db.execute(stmt)
    items = result.scalars().all()
    return [{"title": i.title, "content": i.content} for i in items]
