"""
modules/gemini/prompt_builder.py - Xay dung prompt 4 phan cho Gemini
Day la phan QUAN TRONG NHAT - chat luong prompt = chat luong AI output
"""
import json


# Schema ma Gemini PHAI tra ve
REQUIRED_OUTPUT_SCHEMA = {
    "executive_summary": "string - Tom tat ngan gon tinh hinh",
    "probable_cause": "string - Nguyen nhan co the",
    "confidence": "float 0.0-1.0 - Do tin cay",
    "missing_context": ["string - Danh sach thong tin con thieu"],
    "next_checks": ["string - Cac buoc kiem tra tiep theo"],
    "severity_assessment": "critical|high|medium|low",
    "recommended_action": "string - De xuat hanh dong (chi doc, khong thuc thi)",
    "override_flag": "boolean - false"
}


def build_prompt(
    alert_data: dict,
    normalized_event: dict,
    system_info: dict = None,
    diagnostic_evidence: list = None,
    recent_incidents: list = None,
    known_issues: list = None,
) -> str:
    """
    Xay dung prompt 4 phan bat buoc cho Gemini.
    """

    # PART 1 - Context hien tai
    part1 = f"""[PART 1 - CURRENT CONTEXT]
Alert Data:
{json.dumps(alert_data, indent=2, default=str)}

Normalized Event:
{json.dumps(normalized_event, indent=2, default=str)}

System Info:
{json.dumps(system_info, indent=2, default=str) if system_info else "Not available - system info not yet configured"}

Diagnostic Evidence:
{json.dumps(diagnostic_evidence, indent=2, default=str) if diagnostic_evidence else "Not yet collected - waiting for diagnostic agent"}
"""

    # PART 2 - Memory: 5 incident gan nhat cung service/host
    if recent_incidents and len(recent_incidents) > 0:
        memory_lines = []
        for inc in recent_incidents[:5]:
            line = f"[{inc.get('created_at', 'unknown')}] severity={inc.get('severity', 'unknown')} - action={inc.get('action_taken', 'none')} -> outcome={inc.get('outcome', 'unknown')}"
            memory_lines.append(line)
        part2 = "[PART 2 - MEMORY: 5 RECENT INCIDENTS (same service/host)]\
" + "\
".join(memory_lines)
    else:
        part2 = "[PART 2 - MEMORY]\
No recent incidents for this service/host. This may be the first incident."

    # PART 3 - Known issues
    if known_issues and len(known_issues) > 0:
        ki_lines = [f"- {ki.get('title', '')}: {ki.get('content', '')}" for ki in known_issues[:5]]
        part3 = "[PART 3 - KNOWN ISSUES]\
" + "\
".join(ki_lines)
    else:
        part3 = "[PART 3 - KNOWN ISSUES]\
No known issues matching this incident."

    # PART 4 - Required output schema
    part4 = f"""[PART 4 - REQUIRED OUTPUT SCHEMA]
Ban PHAI tra ve JSON dung format nay. KHONG duoc them field khac.
{json.dumps(REQUIRED_OUTPUT_SCHEMA, indent=2)}
"""

    # System prompt
    system = """[SYSTEM]
Ban la AI agent phan tich incident he thong IT.
Nhiem vu:
1. Phan tich alert va context duoc cung cap
2. Xac dinh nguyen nhan co the (probable cause)
3. Danh gia muc do nghiem trong (severity)
4. Chi ra thong tin con thieu (missing_context)
5. De xuat buoc kiem tra tiep theo (next_checks)

Quy tac BAT BUOC:
- KHONG suy dien khi thieu evidence. Ghi ro missing_context.
- confidence PHAI phan anh dung luong evidence co duoc.
- Neu khong du data -> confidence < 0.4
- Neu co evidence ro rang -> confidence 0.6-0.9
- Chi tra ve JSON dung schema yeu cau. KHONG them text khac.
"""

    return f"{system}\
\
{part1}\
\
{part2}\
\
{part3}\
\
{part4}"
