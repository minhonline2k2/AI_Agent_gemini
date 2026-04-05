import json
import re
from schemas.shared_contract import RCAOutput

def parse_gemini_response(text):
    cleaned = text.strip()
    
    # Bo markdown code blocks
    cleaned = re.sub(r'^```json\s*', '', cleaned)
    cleaned = re.sub(r'^```\s*', '', cleaned)
    cleaned = re.sub(r'\s*```$', '', cleaned)
    cleaned = cleaned.strip()
    
    # Tim JSON object trong text
    match = re.search(r'\{[\s\S]*\}', cleaned)
    if match:
        cleaned = match.group(0)
    
    try:
        data = json.loads(cleaned)
        return RCAOutput(**data)
    except Exception as e:
        raise ValueError(f"Cannot parse: {e}")