from pydantic import BaseModel
from typing import Optional

class IncidentCreate(BaseModel):
    title: str
    severity: str = "medium"
    source: str = "manual"
    impacted_service: Optional[str] = None
    impacted_host: Optional[str] = None
    owner: Optional[str] = None
    raw_payload: Optional[dict] = None

class IncidentUpdate(BaseModel):
    status: Optional[str] = None
    severity: Optional[str] = None
    owner: Optional[str] = None
    title: Optional[str] = None

class IncidentResponse(BaseModel):
    id: str
    title: str
    severity: str
    status: str
    source: str
    fingerprint: Optional[str] = None
    impacted_service: Optional[str] = None
    impacted_host: Optional[str] = None
    owner: Optional[str] = None
    raw_payload: Optional[dict] = None
    normalized_event: Optional[dict] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    class Config:
        from_attributes = True

class IncidentListResponse(BaseModel):
    incidents: list[IncidentResponse] = []
    total: int = 0
