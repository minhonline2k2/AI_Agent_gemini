"""
modules/gemini/response_parser.py - Parse va validate response tu Gemini
Dung Pydantic de dam bao Gemini tra dung format
"""
import json
from schemas.shared_contract import RCAOutput


def parse_gemini_response(response_text: str) -> RCAOutput:
    """
    Parse response tu Gemini thanh RCAOutput schema.
    Neu Gemini tra sai format -> raise ValueError
    """
    try:
        # Loai bo markdown code blocks neu co
        cleaned = response_text.strip()
        if cleaned.startswith("```json"):
            cleaned = cleaned[7:]
        if cleaned.startswith("```"):
            cleaned = cleaned[3:]
        if cleaned.endswith("```"):
            cleaned = cleaned[:-3]
        cleaned = cleaned.strip()

        data = json.loads(cleaned)
        # Validate bang Pydantic
        result = RCAOutput(**data)
        return result

    except json.JSONDecodeError as e:
        raise ValueError(f"Gemini response is not valid JSON: {e}")
    except Exception as e:
        raise ValueError(f"Gemini response does not match schema: {e}")
