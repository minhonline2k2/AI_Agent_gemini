"""
modules/orchestrator/act.py - Buoc ACT (Hanh dong)
Muc 1: chi lam viec AN TOAN (luu DB, hien thi UI, tao diagnostic task)
"""
import uuid
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from models.rca import RCAResult
from models.agent import DiagnosticTask
from modules.audit.logger import audit_log


async def act(
    db: AsyncSession,
    incident_id,
    round_number: int,
    rca_output,
    prompt: str,
    raw_response: str,
    overrides: list,
    context: dict,
):
    """
    Thuc hien hanh dong sau khi AI phan tich:
    1. Luu ket qua RCA vao DB
    2. Tao diagnostic tasks neu can
    3. Ghi audit trail
    """

    # 1. Luu ket qua RCA
    rca = RCAResult(
        id=uuid.uuid4(),
        incident_id=incident_id,
        round_number=round_number,
        perceive_context=context,
        gemini_prompt=prompt,
        gemini_response_raw=raw_response,
        executive_summary=rca_output.executive_summary,
        probable_cause=rca_output.probable_cause,
        confidence=rca_output.confidence,
        missing_context=rca_output.missing_context,
        next_checks=rca_output.next_checks,
        override_applied=rca_output.override_flag,
        override_reason=overrides[0]["reason"] if overrides else None,
        override_details=overrides if overrides else None,
    )
    db.add(rca)

    # 2. Tao diagnostic tasks tu next_checks
    # Chi tao task cho cac tool da co trong registry
    SAFE_TOOLS = [
        "get_hostname", "get_ip_addr", "get_routes", "get_listening_ports",
        "get_disk_usage", "get_memory_usage", "get_top_cpu_processes",
        "get_systemd_service_status", "get_supervisor_status",
        "nginx_config_test", "tail_log", "http_health_check_internal",
    ]

    for check in rca_output.next_checks:
        tool_name = check.split(" ")[0] if " " in check else check
        if tool_name in SAFE_TOOLS:
            task = DiagnosticTask(
                id=uuid.uuid4(),
                incident_id=incident_id,
                tool_name=tool_name,
                tool_input={},
                status="pending",
                timeout_seconds=30,
            )
            db.add(task)

    # 3. Ghi audit trail
    await audit_log(
        db, "rca_completed", "orchestrator", "create",
        resource_type="rca_result", resource_id=rca.id,
        details={
            "round": round_number,
            "confidence": rca_output.confidence,
            "overrides": len(overrides),
        },
    )

    # Ghi override vao audit trail (neu co)
    if overrides:
        await audit_log(
            db, "rca_override", "system_override", "override",
            resource_type="rca_result", resource_id=rca.id,
            details={"overrides": overrides},
        )

    return rca
