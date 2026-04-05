"""api/v1/knowledge.py - CRUD knowledge base"""
import uuid
from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_db
from models.knowledge import KnowledgeBase

router = APIRouter()


@router.get("")
async def list_knowledge(type: str = Query(None), db: AsyncSession = Depends(get_db)):
    stmt = select(KnowledgeBase).where(KnowledgeBase.status == "active")
    if type:
        stmt = stmt.where(KnowledgeBase.type == type)
    result = await db.execute(stmt.order_by(KnowledgeBase.created_at.desc()))
    items = result.scalars().all()
    return {"items": [
        {"id": str(i.id), "type": i.type, "title": i.title, "content": i.content,
         "tags": i.tags, "severity": i.severity, "status": i.status,
         "linked_services": i.linked_services, "created_at": str(i.created_at)}
        for i in items
    ]}


@router.post("")
async def create_knowledge(data: dict, db: AsyncSession = Depends(get_db)):
    item = KnowledgeBase(id=uuid.uuid4(), **data)
    db.add(item)
    return {"status": "created", "id": str(item.id)}
