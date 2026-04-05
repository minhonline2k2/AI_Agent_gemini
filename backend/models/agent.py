"""
models/agent.py - Bang agents va diagnostic_tasks
Agent la private diagnostic agent chay o vung private
"""
import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Integer, DateTime
from sqlalchemy.dialects.postgresql import UUID, JSONB
from database import Base


class Agent(Base):
    __tablename__ = "agents"

    id = Column(String(255), primary_key=True)               # agent_id (VD: agent-mypoint-message1m)
    hostname = Column(String(255))
    version = Column(String(50))
    status = Column(String(20), default="unknown")           # online/offline/unknown
    last_heartbeat = Column(DateTime(timezone=True))
    last_inventory_sync = Column(DateTime(timezone=True))
    registered_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class DiagnosticTask(Base):
    """
    Task giao cho private agent thuc hien
    VD: get_top_cpu_processes, get_disk_usage, ...
    """
    __tablename__ = "diagnostic_tasks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    incident_id = Column(UUID(as_uuid=True), index=True)
    agent_id = Column(String(255))
    tool_name = Column(String(100))                          # Ten tool trong registry
    tool_input = Column(JSONB, default=dict)                 # Tham so dau vao
    status = Column(String(20), default="pending")           # pending/in_progress/completed/failed/timeout
    result = Column(JSONB)                                   # Ket qua tra ve
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    completed_at = Column(DateTime(timezone=True))
    timeout_seconds = Column(Integer, default=30)
