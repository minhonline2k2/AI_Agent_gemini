"""api/v1/rca.py - Trigger RCA thu cong"""
import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_db
from modules.orchestrator.loop import run_analysis_loop

router = APIRouter()


@router.post("/trigger/{incident_id}")
async def trigger_rca(incident_id: str, db: AsyncSession = Depends(get_db)):
    """Trigger phan tich RCA thu cong cho 1 incident"""
    try:
        result = await run_analysis_loop(db, uuid.UUID(incident_id))
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
