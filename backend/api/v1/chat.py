"""api/v1/chat.py - Chat voi AI agent"""
import uuid
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_db
from modules.orchestrator.loop import run_analysis_loop

router = APIRouter()


@router.post("")
async def chat(req: dict, db: AsyncSession = Depends(get_db)):
    """
    Chat voi AI agent.
    Neu co incident_id -> trigger phan tich cho incident do
    Neu khong -> tra loi chung
    """
    message = req.get("message", "")
    incident_id = req.get("incident_id")

    if incident_id:
        # Trigger phan tich cho incident cu the
        result = await run_analysis_loop(db, uuid.UUID(incident_id))
        return {
            "messages": [
                {"role": "user", "content": message},
                {"role": "assistant", "content": result.get("rca", {}).get("executive_summary", "Dang phan tich..."),
                 "step": "reason", "metadata": result},
            ],
            "incident_id": incident_id,
        }

    return {
        "messages": [
            {"role": "user", "content": message},
            {"role": "assistant",
             "content": "Toi la AI Incident Assistant. Hay gui cho toi incident_id de toi phan tich, hoac hoi bat ky cau hoi nao ve van hanh he thong."},
        ]
    }
