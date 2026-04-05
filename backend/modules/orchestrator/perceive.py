"""
modules/orchestrator/perceive.py - Buoc PERCEIVE (Thu thap thong tin)
Thu thap tat ca context lien quan den incident
"""
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession
from models.incident import Incident
from models.system_info import SystemInfo
from models.knowledge import KnowledgeBase
from models.agent import DiagnosticTask


async def gather_context(db: AsyncSession, incident: Incident) -> dict:
    """
    Thu thap context cho 1 incident:
    - Alert data (tu incident)
    - System info (tu system_info table)
    - 5 incident gan nhat cung service/host (memory)
    - Known issues lien quan
    - Diagnostic evidence (neu co)
    """
    context = {
        "alert_data": incident.raw_payload or {},
        "normalized_event": incident.normalized_event or {},
        "system_info": None,
        "recent_incidents": [],
        "known_issues": [],
        "diagnostic_evidence": [],
    }

    # 1. Lay system info cua host bi anh huong
    if incident.impacted_host:
        stmt = select(SystemInfo).where(SystemInfo.hostname == incident.impacted_host)
        result = await db.execute(stmt)
        sys_info = result.scalar_one_or_none()
        if sys_info:
            context["system_info"] = {
                "hostname": sys_info.hostname,
                "ip_addresses": sys_info.ip_addresses,
                "role": sys_info.role,
                "environment": sys_info.environment,
                "criticality": sys_info.criticality,
                "dependencies": sys_info.dependencies,
                "service_catalog": sys_info.service_catalog,
                "known_constraints": sys_info.known_constraints,
                "notes": sys_info.notes,
            }

    # 2. Lay 5 incident gan nhat cung service/host (MEMORY Layer 1)
    conditions = []
    if incident.impacted_host:
        conditions.append(Incident.impacted_host == incident.impacted_host)
    if incident.impacted_service:
        conditions.append(Incident.impacted_service == incident.impacted_service)

    if conditions:
        from sqlalchemy import or_
        stmt = (
            select(Incident)
            .where(or_(*conditions))
            .where(Incident.id != incident.id)
            .order_by(desc(Incident.created_at))
            .limit(5)
        )
        result = await db.execute(stmt)
        recent = result.scalars().all()
        context["recent_incidents"] = [
            {
                "id": str(r.id),
                "title": r.title,
                "severity": r.severity,
                "status": r.status,
                "created_at": str(r.created_at),
                "action_taken": "see audit trail",
                "outcome": r.status,
            }
            for r in recent
        ]

    # 3. Lay known issues lien quan
    stmt = (
        select(KnowledgeBase)
        .where(KnowledgeBase.type == "known_issue")
        .where(KnowledgeBase.status == "active")
        .limit(5)
    )
    result = await db.execute(stmt)
    known = result.scalars().all()
    context["known_issues"] = [
        {"title": k.title, "content": k.content, "severity": k.severity}
        for k in known
    ]

    # 4. Lay diagnostic evidence (ket qua tu private agent)
    stmt = (
        select(DiagnosticTask)
        .where(DiagnosticTask.incident_id == incident.id)
        .where(DiagnosticTask.status == "completed")
        .order_by(DiagnosticTask.completed_at.desc())
    )
    result = await db.execute(stmt)
    tasks = result.scalars().all()
    context["diagnostic_evidence"] = [
        {
            "tool": t.tool_name,
            "result": t.result,
            "executed_at": str(t.completed_at),
        }
        for t in tasks
    ]

    return context
