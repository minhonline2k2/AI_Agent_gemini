"""
api/v1/ingest.py - Nhan alert tu Alertmanager
Endpoint chinh: POST /api/v1/ingest/alertmanager
"""
import uuid
from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from config import settings
from models.incident import Incident
from modules.ingestion.normalizer import normalize_alertmanager
from modules.ingestion.deduplicator import find_existing_incident
from modules.audit.logger import audit_log
from modules.orchestrator.loop import run_analysis_loop

router = APIRouter()


@router.post("/alertmanager")
async def ingest_alertmanager(
    payload: dict,
    db: AsyncSession = Depends(get_db),
    authorization: str = Header(None),
):
    """
    Nhan webhook tu Alertmanager.
    1. Xac thuc token
    2. Chuan hoa alert
    3. Kiem tra dedup
    4. Tao/cap nhat incident
    5. Trigger AI analysis
    """
    # 1. Xac thuc
    expected_token = f"Bearer {settings.INGEST_TOKEN}"
    if authorization != expected_token:
        raise HTTPException(status_code=401, detail="Invalid ingest token")

    # 2. Chuan hoa
    normalized_alerts = normalize_alertmanager(payload)

    created = 0
    updated = 0
    deduped = 0
    ingestion_id = str(uuid.uuid4())

    for alert in normalized_alerts:
        # 3. Kiem tra dedup
        existing = await find_existing_incident(db, alert["fingerprint"])

        if existing:
            # Da co incident -> cap nhat
            if alert["status_from_alert"] == "resolved":
                existing.status = "resolved"
                updated += 1
            else:
                deduped += 1
            continue

        # 4. Tao incident moi
        incident = Incident(
            id=uuid.uuid4(),
            title=alert["title"],
            severity=alert["severity"],
            status="open",
            source=alert["source"],
            fingerprint=alert["fingerprint"],
            impacted_service=alert["impacted_service"],
            impacted_host=alert["impacted_host"],
            raw_payload=alert["raw_alert"],
            normalized_event=alert["normalized_event"],
        )
        db.add(incident)
        await db.flush()  # De co incident.id

        # Ghi audit
        await audit_log(
            db, "incident_created", "alertmanager", "create",
            resource_type="incident", resource_id=incident.id,
            details={"fingerprint": alert["fingerprint"]},
        )

        # 5. Trigger AI analysis (chay async)
        try:
            await run_analysis_loop(db, incident.id)
        except Exception as e:
            print(f"[WARN] RCA failed for {incident.id}: {e}")

        created += 1

    return {
        "ingestion_id": ingestion_id,
        "incidents_created": created,
        "incidents_updated": updated,
        "deduped": deduped,
    }
