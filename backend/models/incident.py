"""
models/incident.py - Bang incidents (su co) va observations
Layer 4 (Memory) + Layer 6 (Operation Agent)
"""
import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Text, Float, Integer, DateTime
from sqlalchemy.dialects.postgresql import UUID, JSONB
from database import Base


class Incident(Base):
    __tablename__ = "incidents"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(Text, nullable=False)                     # Tieu de su co
    severity = Column(String(20), default="medium")          # critical/high/medium/low/info
    status = Column(String(20), default="open")              # open/acknowledged/investigating/resolved/closed
    source = Column(String(50), default="alertmanager")      # alertmanager/manual/api
    fingerprint = Column(String(64), index=True)             # De dedup (khong tao trung)
    impacted_service = Column(String(255))                   # Service bi anh huong
    impacted_host = Column(String(255))                      # Host bi anh huong
    owner = Column(String(255))                              # Nguoi xu ly
    raw_payload = Column(JSONB)                              # Du lieu goc tu alert
    normalized_event = Column(JSONB)                         # Du lieu da chuan hoa
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc),
                        onupdate=lambda: datetime.now(timezone.utc))


class IncidentObservation(Base):
    """
    Bang ghi nhan ket qua thuc te sau moi vong P->R->A->O
    De AI hoc tu kinh nghiem: so sanh du doan vs thuc te
    """
    __tablename__ = "incident_observations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    incident_id = Column(UUID(as_uuid=True), index=True)
    rca_result_id = Column(UUID(as_uuid=True))
    action_taken = Column(Text)           # Hanh dong da lam
    actual_outcome = Column(Text)         # Ket qua thuc te
    prediction_delta = Column(Text)       # Chenh lech giua AI du doan va thuc te
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
