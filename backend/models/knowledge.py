"""
models/knowledge.py - Knowledge base: runbook, known issues, notes
"""
import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Text, DateTime
from sqlalchemy.dialects.postgresql import UUID, JSONB
from database import Base


class KnowledgeBase(Base):
    __tablename__ = "knowledge_base"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    type = Column(String(20), default="runbook")             # runbook/known_issue/note
    title = Column(String(255))
    content = Column(Text)
    tags = Column(JSONB, default=list)
    linked_services = Column(JSONB, default=list)            # Services lien quan
    linked_alert_names = Column(JSONB, default=list)         # Alert names lien quan
    severity = Column(String(20))
    status = Column(String(20), default="active")            # active/archived
    created_by = Column(String(255))
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc),
                        onupdate=lambda: datetime.now(timezone.utc))
