"""api/v1/incidents.py - CRUD incident"""
import uuid
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func, desc
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_db
from models.incident import Incident
from models.rca import RCAResult
from schemas.incident import IncidentResponse, IncidentUpdate, IncidentListResponse
from modules.audit.logger import audit_log

router = APIRouter()


@router.get("", response_model=IncidentListResponse)
async def list_incidents(
    status: str = Query(None),
    severity: str = Query(None),
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    stmt = select(Incident).order_by(desc(Incident.created_at))
    count_stmt = select(func.count(Incident.id))

    if status:
        stmt = stmt.where(Incident.status == status)
        count_stmt = count_stmt.where(Incident.status == status)
    if severity:
        stmt = stmt.where(Incident.severity == severity)
        count_stmt = count_stmt.where(Incident.severity == severity)

    total_result = await db.execute(count_stmt)
    total = total_result.scalar()

    stmt = stmt.offset((page - 1) * per_page).limit(per_page)
    result = await db.execute(stmt)
    incidents = result.scalars().all()

    return IncidentListResponse(
        incidents=[
            IncidentResponse(
                id=str(i.id), title=i.title, severity=i.severity, status=i.status,
                source=i.source, fingerprint=i.fingerprint,
                impacted_service=i.impacted_service, impacted_host=i.impacted_host,
                owner=i.owner, raw_payload=i.raw_payload,
                normalized_event=i.normalized_event,
                created_at=str(i.created_at) if i.created_at else None,
                updated_at=str(i.updated_at) if i.updated_at else None,
            ) for i in incidents
        ],
        total=total,
    )


@router.get("/{incident_id}")
async def get_incident(incident_id: str, db: AsyncSession = Depends(get_db)):
    incident = await db.get(Incident, uuid.UUID(incident_id))
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")

    # Lay RCA results
    stmt = select(RCAResult).where(RCAResult.incident_id == incident.id).order_by(RCAResult.round_number)
    result = await db.execute(stmt)
    rca_results = result.scalars().all()

    return {
        "incident": {
            "id": str(incident.id), "title": incident.title,
            "severity": incident.severity, "status": incident.status,
            "source": incident.source, "impacted_service": incident.impacted_service,
            "impacted_host": incident.impacted_host, "owner": incident.owner,
            "raw_payload": incident.raw_payload, "normalized_event": incident.normalized_event,
            "created_at": str(incident.created_at), "updated_at": str(incident.updated_at),
        },
        "rca_results": [
            {
                "id": str(r.id), "round_number": r.round_number,
                "executive_summary": r.executive_summary, "probable_cause": r.probable_cause,
                "confidence": r.confidence, "missing_context": r.missing_context,
                "next_checks": r.next_checks, "override_applied": r.override_applied,
                "override_reason": r.override_reason, "created_at": str(r.created_at),
            } for r in rca_results
        ],
    }


@router.put("/{incident_id}")
async def update_incident(incident_id: str, req: IncidentUpdate, db: AsyncSession = Depends(get_db)):
    incident = await db.get(Incident, uuid.UUID(incident_id))
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")

    if req.status:
        incident.status = req.status
    if req.severity:
        incident.severity = req.severity
    if req.owner:
        incident.owner = req.owner
    if req.title:
        incident.title = req.title

    await audit_log(db, "incident_updated", "user", "update",
                   resource_type="incident", resource_id=incident.id,
                   details=req.model_dump(exclude_none=True))
    return {"status": "updated"}
