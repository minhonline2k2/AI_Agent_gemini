"""
schemas/shared_contract.py - Schema dung chung giua public backend va private agent
File nay PHAI GIONG voi file shared/contract.py ben private agent
"""
from pydantic import BaseModel, Field
from typing import Optional, Literal


# --- RCA Output (Gemini PHAI tra dung format nay) ---
class RCAOutput(BaseModel):
    executive_summary: str
    probable_cause: str
    confidence: float = Field(ge=0.0, le=1.0)
    missing_context: list[str] = []
    next_checks: list[str] = []
    severity_assessment: Literal["critical", "high", "medium", "low"]
    recommended_action: str = ""
    override_flag: bool = False


# --- Agent Inventory ---
class ListeningPort(BaseModel):
    port: int
    process: str

class DiskUsageItem(BaseModel):
    path: str
    used_pct: float

class TopProcessItem(BaseModel):
    pid: int
    name: str
    cpu_pct: float

class InventorySnapshot(BaseModel):
    os: str = ""
    ip_addresses: list[str] = []
    running_services: list[str] = []
    listening_ports: list[ListeningPort] = []
    disk_usage: list[DiskUsageItem] = []
    memory_usage_pct: float = 0.0
    top_cpu_processes: list[TopProcessItem] = []
    collected_at: str

class InventoryPayload(BaseModel):
    agent_id: str
    hostname: str
    snapshot: InventorySnapshot


# --- Heartbeat ---
class HeartbeatPayload(BaseModel):
    agent_id: str
    hostname: str
    version: str = "1.0.0"
    status: str = "healthy"
    timestamp: str


# --- Diagnostic Result ---
class DiagnosticResultPayload(BaseModel):
    task_id: str
    agent_id: str
    tool_name: str
    status: Literal["success", "failed", "timeout"]
    output: dict = {}
    executed_at: str
    duration_ms: int


# --- Tool Definition ---
class ToolDefinition(BaseModel):
    name: str
    description: str
    risk_level: Literal["safe", "moderate", "dangerous"]
    approval_required: bool = False
    auto_execute: bool = True
    timeout_seconds: int = 30
    input_schema: dict = {}
    output_schema: dict = {}
    enabled: bool = True
