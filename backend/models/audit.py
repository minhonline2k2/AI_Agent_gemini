"""
models/audit.py - Nhat ky kiem tra (audit trail)
Ghi lai MOI thao tac trong he thong
"""
import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime
from sqlalchemy.dialects.postgresql import UUID, JSONB
from database import Base


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    event_type = Column(String(100))        # VD: incident_created, rca_completed, override
    actor = Column(String(255))             # Ai lam: username hoac system
    actor_type = Column(String(20), default="system")  # user/system/agent
    resource_type = Column(String(100))     # VD: incident, rca_result, diagnostic_task
    resource_id = Column(UUID(as_uuid=True))
    action = Column(String(100))            # VD: create, update, delete, override
    details = Column(JSONB)                 # Chi tiet them
    ip_address = Column(String(50))
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
