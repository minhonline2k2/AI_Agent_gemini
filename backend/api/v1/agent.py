"""
api/v1/agent.py - API cho private diagnostic agent
Task queue, heartbeat, results, inventory
"""
import uuid
import hmac
import hashlib
import time
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from config import settings
from models.agent import Agent, DiagnosticTask
from models.system_info import SystemInfo
from schemas.shared_contract import HeartbeatPayload, DiagnosticResultPayload, InventoryPayload
from modules.audit.logger import audit_log

router = APIRouter()


def verify_hmac(agent_id: str, timestamp: str, nonce: str, signature: str):
    """Xac thuc HMAC tu private agent"""
    # Kiem tra timestamp (±5 phut)
    try:
        ts = int(timestamp)
        now = int(time.time())
        if abs(now - ts) > 300:
            raise HTTPException(status_code=401, detail="Timestamp expired")
    except ValueError:
        raise HTTPException(status_code=401, detail="Invalid timestamp")

    # Tinh HMAC va so sanh
    message = f"{agent_id}{timestamp}{nonce}"
    expected = hmac.new(
        settings.AGENT_SECRET.encode(), message.encode(), hashlib.sha256
    ).hexdigest()

    if not hmac.compare_digest(signature, expected):
        raise HTTPException(status_code=401, detail="Invalid HMAC signature")


@router.get("/tasks")
async def get_tasks(
    db: AsyncSession = Depends(get_db),
    x_agent_id: str = Header(None),
    x_timestamp: str = Header(None),
    x_nonce: str = Header(None),
    x_signature: str = Header(None),
):
    """Private agent poll lay task"""
    verify_hmac(x_agent_id, x_timestamp, x_nonce, x_signature)

    stmt = (
        select(DiagnosticTask)
        .where(DiagnosticTask.status == "pending")
        .order_by(DiagnosticTask.created_at)
        .limit(5)
    )
    result = await db.execute(stmt)
    tasks = result.scalars().all()

    # Danh dau in_progress
    for t in tasks:
        t.status = "in_progress"
        t.agent_id = x_agent_id

    return {
        "tasks": [
            {
                "task_id": str(t.id),
                "task_type": "diagnostic",
                "tool_name": t.tool_name,
                "tool_input": t.tool_input or {},
                "incident_id": str(t.incident_id),
                "created_at": str(t.created_at),
                "timeout_seconds": t.timeout_seconds,
            }
            for t in tasks
        ]
    }


@router.post("/results")
async def submit_result(
    payload: DiagnosticResultPayload,
    db: AsyncSession = Depends(get_db),
    x_agent_id: str = Header(None),
    x_timestamp: str = Header(None),
    x_nonce: str = Header(None),
    x_signature: str = Header(None),
):
    """Private agent gui ket qua diagnostic"""
    verify_hmac(x_agent_id, x_timestamp, x_nonce, x_signature)

    task = await db.get(DiagnosticTask, uuid.UUID(payload.task_id))
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    task.status = payload.status
    task.result = payload.output
    task.completed_at = datetime.now(timezone.utc)

    await audit_log(
        db, "diagnostic_completed", x_agent_id, "update",
        resource_type="diagnostic_task", resource_id=task.id,
        details={"tool": payload.tool_name, "status": payload.status},
        actor_type="agent",
    )

    return {"result_id": str(uuid.uuid4()), "accepted": True}


@router.post("/heartbeat")
async def heartbeat(
    payload: HeartbeatPayload,
    db: AsyncSession = Depends(get_db),
    x_agent_id: str = Header(None),
    x_timestamp: str = Header(None),
    x_nonce: str = Header(None),
    x_signature: str = Header(None),
):
    """Private agent gui heartbeat"""
    verify_hmac(x_agent_id, x_timestamp, x_nonce, x_signature)

    agent = await db.get(Agent, payload.agent_id)
    if not agent:
        agent = Agent(
            id=payload.agent_id,
            hostname=payload.hostname,
            version=payload.version,
            status="online",
            last_heartbeat=datetime.now(timezone.utc),
        )
        db.add(agent)
    else:
        agent.status = "online"
        agent.hostname = payload.hostname
        agent.version = payload.version
        agent.last_heartbeat = datetime.now(timezone.utc)

    return {"status": "ok"}


@router.post("/inventory")
async def sync_inventory(
    payload: InventoryPayload,
    db: AsyncSession = Depends(get_db),
    x_agent_id: str = Header(None),
    x_timestamp: str = Header(None),
    x_nonce: str = Header(None),
    x_signature: str = Header(None),
):
    """Private agent dong bo inventory"""
    verify_hmac(x_agent_id, x_timestamp, x_nonce, x_signature)

    stmt = select(SystemInfo).where(SystemInfo.hostname == payload.hostname)
    result = await db.execute(stmt)
    info = result.scalar_one_or_none()

    snap = payload.snapshot
    if not info:
        info = SystemInfo(
            id=uuid.uuid4(),
            hostname=payload.hostname,
            ip_addresses=snap.ip_addresses,
            synced_from_agent=True,
        )
        db.add(info)
    else:
        info.ip_addresses = snap.ip_addresses
        info.synced_from_agent = True

    # Update agent last_inventory_sync
    agent = await db.get(Agent, payload.agent_id)
    if agent:
        agent.last_inventory_sync = datetime.now(timezone.utc)

    return {"status": "synced"}
