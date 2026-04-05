import json
import re
import google.generativeai as genai
from config import settings

if settings.GEMINI_API_KEY and not settings.GEMINI_API_KEY.startswith("thay"):
    genai.configure(api_key=settings.GEMINI_API_KEY)

def _clean_json(text):
    cleaned = text.strip()
    cleaned = re.sub(r'^```json\s*', '', cleaned)
    cleaned = re.sub(r'^```\s*', '', cleaned)
    cleaned = re.sub(r'\s*```$', '', cleaned)
    cleaned = cleaned.strip()
    match = re.search(r'\{[\s\S]*\}', cleaned)
    if match:
        cleaned = match.group(0)
    return cleaned

def _mock():
    return json.dumps({
        "executive_summary": "CPU spike. Can thu thap process list va logs.",
        "probable_cause": "Unknown - chua du evidence",
        "confidence": 0.35,
        "missing_context": ["Top CPU processes", "Application logs"],
        "next_checks": ["get_top_cpu_processes", "tail_log"],
        "severity_assessment": "high",
        "recommended_action": "Thu thap evidence",
        "override_flag": False
    })

async def call_gemini(prompt):
    if not settings.GEMINI_API_KEY or settings.GEMINI_API_KEY.startswith("thay"):
        return _mock()
    try:
        model = genai.GenerativeModel(settings.GEMINI_MODEL)
        r = model.generate_content(
            prompt + "\n\nRespond with ONLY a raw JSON object. No markdown. No backticks. Start with { end with }.",
            generation_config={"temperature": 0.1, "max_output_tokens": 8192}
        )
        cleaned = _clean_json(r.text)
        json.loads(cleaned)
        return cleaned
    except Exception as e:
        print(f"[GEMINI] Error: {e}")
        return json.dumps({
            "executive_summary": f"AI error: {str(e)[:100]}",
            "probable_cause": "Analysis pending",
            "confidence": 0.0,
            "missing_context": ["AI analysis pending"],
            "next_checks": ["Retry analysis"],
            "severity_assessment": "medium",
            "recommended_action": "Wait and retry",
            "override_flag": False
        })