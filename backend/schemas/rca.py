from pydantic import BaseModel
from typing import Optional

class RCAResultResponse(BaseModel):
    id: str
    incident_id: str
    round_number: int
    executive_summary: Optional[str] = None
    probable_cause: Optional[str] = None
    confidence: float = 0.0
    missing_context: list[str] = []
    next_checks: list[str] = []
    override_applied: bool = False
    override_reason: Optional[str] = None
    created_at: Optional[str] = None
    class Config:
        from_attributes = True
