import uuid
import json
from datetime import datetime, timezone
from fastapi import APIRouter, Depends
from sqlalchemy import select, desc, func, or_
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_db
from config import settings
from models.incident import Incident
from models.rca import RCAResult
from models.system_info import SystemInfo
from models.knowledge import KnowledgeBase
from models.agent import Agent, DiagnosticTask
from models.audit import AuditLog
from modules.orchestrator.loop import run_analysis_loop
from modules.audit.logger import audit_log

router = APIRouter()

# 12 tools agent co the chay
AVAILABLE_TOOLS = {
    "get_hostname": "Lay hostname server",
    "get_ip_addr": "Lay dia chi IP",
    "get_routes": "Xem routing table",
    "get_listening_ports": "Xem ports dang listen",
    "get_disk_usage": "Xem dung luong disk",
    "get_memory_usage": "Xem RAM",
    "get_top_cpu_processes": "Top processes dung CPU",
    "get_systemd_service_status": "Trang thai 1 systemd service",
    "get_supervisor_status": "Trang thai supervisor",
    "nginx_config_test": "Test cau hinh nginx",
    "tail_log": "Doc log file",
    "http_health_check_internal": "Kiem tra health endpoint",
}


async def query_system_data(db: AsyncSession, query_type: str, params: dict = {}) -> str:
    """Truy van du lieu he thong tu DB"""

    if query_type == "incidents_summary":
        total = (await db.execute(select(func.count(Incident.id)))).scalar() or 0
        openx = (await db.execute(select(func.count(Incident.id)).where(
            Incident.status.in_(["open", "acknowledged", "investigating"])))).scalar() or 0
        crit = (await db.execute(select(func.count(Incident.id)).where(
            Incident.severity == "critical"))).scalar() or 0
        return f"Tong: {total} incidents, {openx} dang open, {crit} critical"

    elif query_type == "incidents_list":
        r = await db.execute(
            select(Incident).order_by(desc(Incident.created_at)).limit(10))
        items = r.scalars().all()
        lines = [f"- [{i.severity}] {i.title} | host={i.impacted_host} | status={i.status}"
                 for i in items]
        return "\n".join(lines) if lines else "Khong co incident nao"

    elif query_type == "server_info":
        hostname = params.get("hostname", "")
        if hostname:
            r = await db.execute(select(SystemInfo).where(
                SystemInfo.hostname.ilike(f"%{hostname}%")))
        else:
            r = await db.execute(select(SystemInfo).order_by(SystemInfo.hostname))
        items = r.scalars().all()
        if not items:
            return f"Khong tim thay server '{hostname}'"
        lines = []
        for s in items:
            lines.append(f"Hostname: {s.hostname}")
            lines.append(f"  IP: {', '.join(s.ip_addresses or [])}")
            lines.append(f"  Role: {s.role}")
            lines.append(f"  Criticality: {s.criticality}")
            lines.append(f"  Environment: {s.environment}")
            if s.dependencies:
                lines.append(f"  Dependencies: {json.dumps(s.dependencies)}")
            if s.notes:
                lines.append(f"  Notes: {s.notes}")
            lines.append(f"  Agent synced: {s.synced_from_agent}")
            lines.append("")
        return "\n".join(lines)

    elif query_type == "server_list":
        r = await db.execute(select(SystemInfo).order_by(SystemInfo.criticality, SystemInfo.hostname))
        items = r.scalars().all()
        lines = [f"- {s.hostname} | {s.role} | {s.criticality} | IP: {','.join(s.ip_addresses or [])}"
                 for s in items]
        return "\n".join(lines) if lines else "Chua co server nao trong he thong"

    elif query_type == "agents_status":
        r = await db.execute(select(Agent))
        agents = r.scalars().all()
        if not agents:
            return "Chua co agent nao dang ky. Can cai Private Diagnostic Agent tren server private."
        lines = [f"- {a.id} | {a.hostname} | status={a.status} | last_heartbeat={a.last_heartbeat}"
                 for a in agents]
        return "\n".join(lines)

    elif query_type == "knowledge":
        r = await db.execute(select(KnowledgeBase).where(KnowledgeBase.status == "active"))
        items = r.scalars().all()
        lines = [f"- [{k.type}] {k.title}: {(k.content or '')[:100]}" for k in items]
        return "\n".join(lines) if lines else "Chua co knowledge base"

    elif query_type == "incident_detail":
        inc_id = params.get("incident_id", "")
        try:
            inc = await db.get(Incident, uuid.UUID(inc_id))
        except:
            # Tim theo title
            r = await db.execute(select(Incident).where(
                Incident.title.ilike(f"%{inc_id}%")).limit(1))
            inc = r.scalar_one_or_none()
        if not inc:
            return f"Khong tim thay incident '{inc_id}'"
        r2 = await db.execute(select(RCAResult).where(
            RCAResult.incident_id == inc.id).order_by(RCAResult.round_number))
        rcas = r2.scalars().all()
        text = f"""Incident: {inc.title}
Severity: {inc.severity} | Status: {inc.status}
Host: {inc.impacted_host} | Service: {inc.impacted_service}
Created: {inc.created_at}
"""
        for r in rcas:
            text += f"""
--- RCA Round {r.round_number} ---
Summary: {r.executive_summary}
Cause: {r.probable_cause}
Confidence: {int(r.confidence * 100)}%
Missing: {', '.join(r.missing_context or [])}
Next: {', '.join(r.next_checks or [])}
Override: {r.override_reason or 'None'}
"""
        return text

    elif query_type == "diagnostic_results":
        hostname = params.get("hostname", "")
        # Tim incident lien quan den host
        r = await db.execute(
            select(DiagnosticTask).where(DiagnosticTask.status == "completed")
            .order_by(desc(DiagnosticTask.completed_at)).limit(10))
        tasks = r.scalars().all()
        if not tasks:
            return "Chua co diagnostic result nao. Can cai Private Agent va tao diagnostic task."
        lines = [f"- Tool: {t.tool_name} | Status: {t.status} | Result: {json.dumps(t.result or {})[:200]}"
                 for t in tasks]
        return "\n".join(lines)

    return "Khong hieu query type"


async def create_diagnostic_task(db: AsyncSession, tool_name: str, tool_input: dict = {},
                                  target_host: str = None) -> str:
    """Tao diagnostic task cho private agent thuc hien"""
    if tool_name not in AVAILABLE_TOOLS:
        return f"Tool '{tool_name}' khong hop le. Tools kha dung: {', '.join(AVAILABLE_TOOLS.keys())}"

    # Tim agent online
    r = await db.execute(select(Agent).where(Agent.status == "online").limit(1))
    agent = r.scalar_one_or_none()

    if not agent:
        return "Khong co agent nao dang online. Can cai va chay Private Diagnostic Agent truoc."

    # Tao task
    task = DiagnosticTask(
        id=uuid.uuid4(),
        incident_id=None,
        agent_id=agent.id,
        tool_name=tool_name,
        tool_input=tool_input,
        status="pending",
        timeout_seconds=30,
    )
    db.add(task)

    await audit_log(db, "diagnostic_requested", "chat_user", "create",
                    resource_type="diagnostic_task", resource_id=task.id,
                    details={"tool": tool_name, "input": tool_input, "target": target_host})

    return f"Da tao task: {tool_name} (ID: {task.id}). Agent '{agent.id}' se thuc hien trong vong 15 giay. Hoi lai sau 15-30 giay de xem ket qua."


async def ai_chat(db: AsyncSession, message: str) -> str:
    """Goi Gemini de hieu intent va tra loi"""
    import google.generativeai as genai

    if not settings.GEMINI_API_KEY or settings.GEMINI_API_KEY.startswith("thay"):
        return "Gemini API key chua cau hinh."

    genai.configure(api_key=settings.GEMINI_API_KEY)

    # Thu thap context
    inc_summary = await query_system_data(db, "incidents_summary")
    srv_list = await query_system_data(db, "server_list")
    agent_status = await query_system_data(db, "agents_status")

    tools_desc = "\n".join([f"- {k}: {v}" for k, v in AVAILABLE_TOOLS.items()])

    prompt = f"""Ban la AI Incident Management Assistant. Tra loi bang tieng Viet.

=== DU LIEU HE THONG HIEN TAI ===
{inc_summary}

Servers:
{srv_list}

Agents:
{agent_status}

Available diagnostic tools:
{tools_desc}

=== HUONG DAN TRA LOI ===
1. Neu nguoi hoi ve server/he thong -> tra loi tu du lieu tren
2. Neu nguoi yeu cau kiem tra server (disk, cpu, memory, log, port...) -> tra loi:
   EXECUTE_TOOL: tool_name | param1=value1
   VD: "EXECUTE_TOOL: get_disk_usage" hoac "EXECUTE_TOOL: get_systemd_service_status | service_name=nginx"
3. Neu nguoi hoi ve incident cu the -> tra loi:
   QUERY_INCIDENT: incident_id_hoac_keyword
4. Neu nguoi hoi chung -> tra loi binh thuong tu kien thuc cua ban
5. Tra loi ngan gon, thuc te, di thang vao van de
6. Neu khong biet -> noi ro khong biet, de nghi kiem tra them

=== CAU HOI CUA NGUOI DUNG ===
{message}"""

    try:
        model = genai.GenerativeModel(settings.GEMINI_MODEL)
        response = model.generate_content(
            prompt,
            generation_config={"temperature": 0.3, "max_output_tokens": 4096}
        )
        return response.text.strip()
    except Exception as e:
        return f"Loi Gemini: {str(e)[:200]}"


@router.post("")
async def chat(req: dict, db: AsyncSession = Depends(get_db)):
    message = (req.get("message") or "").strip()

    incident_id = (req.get("incident_id") or "").strip()

    if not message:
        return {"messages": [{"role": "assistant", "content": "Hay nhap cau hoi hoac yeu cau."}]}

    messages_out = [{"role": "user", "content": message}]

    # Truong hop 1: Co incident_id -> phan tich incident
    if incident_id:
        try:
            result = await run_analysis_loop(db, uuid.UUID(incident_id))
            rca = result.get("rca", {})
            reply = f"""**Phan tich Incident** (Round {result.get('round', '?')}):

**Tom tat:** {rca.get('executive_summary', 'N/A')}
**Nguyen nhan:** {rca.get('probable_cause', 'N/A')}
**Confidence:** {int(rca.get('confidence', 0) * 100)}%
**Thieu:** {', '.join(rca.get('missing_context', [])) or 'Khong'}
**Kiem tra tiep:** {', '.join(rca.get('next_checks', [])) or 'Khong'}"""
            messages_out.append({"role": "assistant", "content": reply, "step": "reason"})
            return {"messages": messages_out, "incident_id": incident_id}
        except Exception as e:
            messages_out.append({"role": "assistant", "content": f"Loi: {e}"})
            return {"messages": messages_out}

    # Truong hop 2: Goi AI de hieu intent
    ai_response = await ai_chat(db, message)

    # Xu ly cac lenh dac biet AI tra ve
    if "EXECUTE_TOOL:" in ai_response:
        # AI yeu cau chay tool
        lines = ai_response.split("\n")
        tool_line = [l for l in lines if "EXECUTE_TOOL:" in l]
        if tool_line:
            parts = tool_line[0].split("EXECUTE_TOOL:")[1].strip().split("|")
            tool_name = parts[0].strip()
            tool_input = {}
            if len(parts) > 1:
                for p in parts[1:]:
                    if "=" in p:
                        k, v = p.strip().split("=", 1)
                        tool_input[k.strip()] = v.strip()

            task_result = await create_diagnostic_task(db, tool_name, tool_input)

            # Lay phan giai thich truoc EXECUTE_TOOL
            explanation = ai_response.split("EXECUTE_TOOL:")[0].strip()
            if explanation:
                messages_out.append({"role": "assistant", "content": explanation})
            messages_out.append({
                "role": "assistant",
                "content": f"🔧 {task_result}",
                "step": "act"
            })
            return {"messages": messages_out}

    elif "QUERY_INCIDENT:" in ai_response:
        # AI yeu cau query incident
        keyword = ai_response.split("QUERY_INCIDENT:")[1].strip().split("\n")[0]
        detail = await query_system_data(db, "incident_detail", {"incident_id": keyword})

        explanation = ai_response.split("QUERY_INCIDENT:")[0].strip()
        if explanation:
            messages_out.append({"role": "assistant", "content": explanation})
        messages_out.append({"role": "assistant", "content": detail})
        return {"messages": messages_out}

    # Truong hop binh thuong: AI tra loi truc tiep
    messages_out.append({"role": "assistant", "content": ai_response})
    return {"messages": messages_out}