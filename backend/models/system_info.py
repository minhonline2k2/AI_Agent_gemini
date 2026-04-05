"""
models/system_info.py - Thong tin he thong + Quyet dinh kien truc (ADR)
Layer 0 (Design Memory) + Layer 2 (Operational Memory)
"""
import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Text, Boolean, DateTime
from sqlalchemy.dialects.postgresql import UUID, JSONB
from database import Base


class SystemInfo(Base):
    """Thong tin cua tung server/service trong he thong"""
    __tablename__ = "system_info"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    hostname = Column(String(255), unique=True, index=True)
    ip_addresses = Column(JSONB, default=list)
    role = Column(String(255))                               # VD: "message queue processor"
    environment = Column(String(50), default="prod")         # prod/staging/dev
    criticality = Column(String(20), default="medium")       # critical/high/medium/low
    owner = Column(String(255))
    escalation_contact = Column(String(255))
    service_catalog = Column(JSONB, default=list)
    dependencies = Column(JSONB, default=dict)               # upstream/downstream
    log_paths = Column(JSONB, default=list)
    metrics_sources = Column(JSONB, default=list)
    known_constraints = Column(Text)
    maintenance_window = Column(Text)
    notes = Column(Text)
    synced_from_agent = Column(Boolean, default=False)       # True neu tu agent dong bo
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc),
                        onupdate=lambda: datetime.now(timezone.utc))


class ArchitectureDecision(Base):
    """
    Architecture Decision Record (ADR)
    Ghi lai ly do cac quyet dinh kien truc quan trong
    Day la Layer 0 - Design Memory
    """
    __tablename__ = "architecture_decisions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String(255))
    context = Column(Text)                                   # Boi canh quyet dinh
    decision = Column(Text)                                  # Quyet dinh la gi
    rationale = Column(Text)                                 # Tai sao chon nhu vay
    consequences = Column(Text)                              # Hau qua / anh huong
    status = Column(String(20), default="active")            # active/deprecated/superseded
    component = Column(String(255))                          # Component lien quan
    created_by = Column(String(255))
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc),
                        onupdate=lambda: datetime.now(timezone.utc))
