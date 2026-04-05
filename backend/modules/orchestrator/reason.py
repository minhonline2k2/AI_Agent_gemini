"""
modules/orchestrator/reason.py - Buoc REASON (Suy luan)
Goi Gemini + Override logic + Validate
"""
import json
from schemas.shared_contract import RCAOutput
from modules.gemini.client import call_gemini
from modules.gemini.prompt_builder import build_prompt
from modules.gemini.response_parser import parse_gemini_response


async def reason(context: dict) -> tuple:
    """
    1. Xay dung prompt tu context
    2. Goi Gemini
    3. Parse response
    4. Ap dung override logic
    5. Tra ve (rca_output, prompt_text, raw_response, overrides)
    """
    # Buoc 1: Xay dung prompt
    prompt = build_prompt(
        alert_data=context.get("alert_data", {}),
        normalized_event=context.get("normalized_event", {}),
        system_info=context.get("system_info"),
        diagnostic_evidence=context.get("diagnostic_evidence"),
        recent_incidents=context.get("recent_incidents"),
        known_issues=context.get("known_issues"),
    )

    # Buoc 2: Goi Gemini
    raw_response = await call_gemini(prompt)

    # Buoc 3: Parse va validate
    try:
        rca_output = parse_gemini_response(raw_response)
    except ValueError as e:
        # Neu parse loi -> tao default output
        rca_output = RCAOutput(
            executive_summary=f"Parse error: {str(e)}",
            probable_cause="Unable to parse AI response",
            confidence=0.0,
            missing_context=["Valid AI response"],
            next_checks=["Retry analysis"],
            severity_assessment="medium",
        )

    # Buoc 4: Override logic BAT BUOC
    overrides = apply_override_logic(rca_output, context)

    return rca_output, prompt, raw_response, overrides


def apply_override_logic(ai_result: RCAOutput, context: dict) -> list:
    """
    Override logic: mot so rule CUNG khong duoc AI thay doi.
    VD: disk > 95% -> BAT BUOC severity = critical

    Override PHAI ghi vao audit trail.
    """
    overrides = []
    evidence = context.get("diagnostic_evidence", [])

    # Rule 1: Disk > 95% -> critical
    for ev in evidence:
        result = ev.get("result", {})
        if ev.get("tool") == "get_disk_usage" and isinstance(result, dict):
            for disk in result.get("disks", []):
                if disk.get("used_pct", 0) > 95 and ai_result.severity_assessment != "critical":
                    overrides.append({
                        "field": "severity_assessment",
                        "original": ai_result.severity_assessment,
                        "new_value": "critical",
                        "reason": f"disk_usage {disk.get('used_pct')}% > 95% threshold",
                    })
                    ai_result.severity_assessment = "critical"

    # Rule 2: OOM detected -> boost confidence
    for ev in evidence:
        result_str = json.dumps(ev.get("result", {})).lower()
        if "oom" in result_str or "out of memory" in result_str:
            if ai_result.confidence < 0.7:
                overrides.append({
                    "field": "confidence",
                    "original": ai_result.confidence,
                    "new_value": 0.85,
                    "reason": "OOM kill event detected in evidence",
                })
                ai_result.confidence = 0.85

    # Rule 3: Kiem tra tu alert labels
    alert_data = context.get("alert_data", {})
    for alert in alert_data.get("alerts", [alert_data]):
        labels = alert.get("labels", {})
        if labels.get("severity") == "critical" and ai_result.severity_assessment != "critical":
            overrides.append({
                "field": "severity_assessment",
                "original": ai_result.severity_assessment,
                "new_value": "critical",
                "reason": "Alert source severity is critical",
            })
            ai_result.severity_assessment = "critical"

    if overrides:
        ai_result.override_flag = True

    return overrides
