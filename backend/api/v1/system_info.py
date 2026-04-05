"""api/v1/system_info.py - CRUD system info + ADR"""
import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_db
from models.system_info import SystemInfo, ArchitectureDecision

router = APIRouter()


@router.get("")
async def list_system_info(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(SystemInfo).order_by(SystemInfo.hostname))
    items = result.scalars().all()
    return {"items": [
        {"id": str(i.id), "hostname": i.hostname, "ip_addresses": i.ip_addresses,
         "role": i.role, "environment": i.environment, "criticality": i.criticality,
         "owner": i.owner, "dependencies": i.dependencies, "notes": i.notes,
         "synced_from_agent": i.synced_from_agent}
        for i in items
    ]}


@router.post("")
async def create_system_info(data: dict, db: AsyncSession = Depends(get_db)):
    info = SystemInfo(id=uuid.uuid4(), **data)
    db.add(info)
    return {"status": "created", "id": str(info.id)}


@router.get("/adr")
async def list_adr(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(ArchitectureDecision).order_by(ArchitectureDecision.created_at.desc()))
    items = result.scalars().all()
    return {"items": [
        {"id": str(i.id), "title": i.title, "context": i.context, "decision": i.decision,
         "rationale": i.rationale, "status": i.status, "component": i.component,
         "created_at": str(i.created_at)}
        for i in items
    ]}


@router.post("/adr")
async def create_adr(data: dict, db: AsyncSession = Depends(get_db)):
    adr = ArchitectureDecision(id=uuid.uuid4(), **data)
    db.add(adr)
    return {"status": "created", "id": str(adr.id)}
