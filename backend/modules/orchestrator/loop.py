"""
modules/orchestrator/loop.py - Vong lap chinh P -> R -> A -> O
Day la "bo nao" cua he thong - dieu phoi toan bo qua trinh phan tich
"""
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from models.incident import Incident
from models.rca import RCAResult
from modules.orchestrator.perceive import gather_context
from modules.orchestrator.reason import reason
from modules.orchestrator.act import act
from modules.orchestrator.observe import observe


async def run_analysis_loop(db: AsyncSession, incident_id) -> dict:
    """
    Chay 1 vong P -> R -> A -> O cho incident.

    Returns:
        dict voi ket qua tung buoc de hien thi tren UI
    """
    steps = []

    # Lay incident tu DB
    incident = await db.get(Incident, incident_id)
    if not incident:
        return {"error": "Incident not found"}

    # Xac dinh day la vong thu may
    stmt = select(func.count()).where(RCAResult.incident_id == incident_id)
    result = await db.execute(stmt)
    current_round = result.scalar() + 1

    # === PERCEIVE ===
    steps.append({"step": "perceive", "status": "running", "detail": "Dang thu thap context..."})
    context = await gather_context(db, incident)
    steps.append({
        "step": "perceive",
        "status": "completed",
        "detail": f"Da thu thap: system_info={'co' if context['system_info'] else 'chua co'}, "
                  f"memory={len(context['recent_incidents'])} incidents, "
                  f"evidence={len(context['diagnostic_evidence'])} results",
    })

    # === REASON ===
    steps.append({"step": "reason", "status": "running", "detail": "Dang goi AI phan tich..."})
    rca_output, prompt, raw_response, overrides = await reason(context)
    steps.append({
        "step": "reason",
        "status": "completed",
        "detail": f"AI tra ve: confidence={rca_output.confidence}, "
                  f"cause='{rca_output.probable_cause[:80]}...', "
                  f"overrides={len(overrides)}",
    })

    # === ACT ===
    steps.append({"step": "act", "status": "running", "detail": "Dang luu ket qua..."})
    rca = await act(db, incident_id, current_round, rca_output, prompt, raw_response, overrides, context)
    steps.append({
        "step": "act",
        "status": "completed",
        "detail": f"Da luu RCA round {current_round}, tao diagnostic tasks cho next_checks",
    })

    # === OBSERVE ===
    steps.append({"step": "observe", "status": "running", "detail": "Dang ghi nhan observation..."})
    obs = await observe(db, incident_id, rca.id)
    steps.append({
        "step": "observe",
        "status": "completed",
        "detail": "Da ghi observation. Data se feed lai cho lan phan tich sau.",
    })

    # Cap nhat incident status
    if incident.status == "open":
        incident.status = "investigating"

    return {
        "incident_id": str(incident_id),
        "round": current_round,
        "steps": steps,
        "rca": {
            "executive_summary": rca_output.executive_summary,
            "probable_cause": rca_output.probable_cause,
            "confidence": rca_output.confidence,
            "missing_context": rca_output.missing_context,
            "next_checks": rca_output.next_checks,
            "severity_assessment": rca_output.severity_assessment,
            "override_applied": rca_output.override_flag,
        },
    }
