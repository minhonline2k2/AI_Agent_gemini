"""
modules/gemini/client.py - Goi Gemini AI API
Co retry + timeout + error handling
"""
import json
import google.generativeai as genai
from config import settings

# Cau hinh Gemini API key
if settings.GEMINI_API_KEY:
    genai.configure(api_key=settings.GEMINI_API_KEY)


async def call_gemini(prompt: str) -> str:
    """
    Goi Gemini API voi prompt da xay dung.
    Tra ve response text.

    Neu khong co API key -> tra ve mock response de demo.
    """
    if not settings.GEMINI_API_KEY or settings.GEMINI_API_KEY.startswith("thay-bang"):
        # Mock response khi chua co API key (de dev/demo)
        return json.dumps({
            "executive_summary": "CPU spike ket hop voi service response cham. Can thu thap them process list va logs de xac dinh nguyen nhan.",
            "probable_cause": "Unknown - khong du evidence. Can kiem tra process list, service logs, va upstream dependencies.",
            "confidence": 0.35,
            "missing_context": [
                "Top CPU processes",
                "Application logs (last 100 lines)",
                "Systemd service status",
                "Upstream service health"
            ],
            "next_checks": [
                "get_top_cpu_processes",
                "tail_log /var/log/app.log",
                "get_systemd_service_status app",
                "http_health_check_internal http://upstream:8080/health"
            ],
            "severity_assessment": "high",
            "recommended_action": "Thu thap evidence tu diagnostic agent, sau do phan tich lai.",
            "override_flag": False
        })

    try:
        model = genai.GenerativeModel(settings.GEMINI_MODEL)
        response = model.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(
                response_mime_type="application/json",
                temperature=0.1,  # Thap = it sang tao, nhieu logic
            ),
        )
        return response.text
    except Exception as e:
        # Neu Gemini loi -> tra ve error response
        return json.dumps({
            "executive_summary": f"Gemini API error: {str(e)}",
            "probable_cause": "Unable to analyze - AI service unavailable",
            "confidence": 0.0,
            "missing_context": ["Gemini API unavailable"],
            "next_checks": ["Retry Gemini call", "Check API key"],
            "severity_assessment": "medium",
            "recommended_action": "Retry analysis when Gemini is available",
            "override_flag": False
        })
