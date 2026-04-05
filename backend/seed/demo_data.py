"""
seed/demo_data.py - Nap du lieu demo vao database
Chay: docker compose exec backend python -m seed.demo_data
"""
import uuid
import asyncio
from datetime import datetime, timezone, timedelta
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


async def seed():
    from database import async_session_factory, init_db
    await init_db()

    async with async_session_factory() as db:
        from models.user import User
        from models.incident import Incident
        from models.rca import RCAResult
        from models.system_info import SystemInfo, ArchitectureDecision
        from models.knowledge import KnowledgeBase
        from models.agent import Agent, DiagnosticTask

        # === USERS ===
        users = [
            User(id=uuid.uuid4(), username="admin", password_hash=pwd_context.hash("admin123"),
                 role="admin", display_name="Administrator", email="admin@example.com"),
            User(id=uuid.uuid4(), username="operator", password_hash=pwd_context.hash("operator123"),
                 role="operator", display_name="Operator", email="ops@example.com"),
            User(id=uuid.uuid4(), username="viewer", password_hash=pwd_context.hash("viewer123"),
                 role="viewer", display_name="Viewer", email="viewer@example.com"),
        ]
        for u in users:
            db.add(u)

        # === SYSTEM INFO (10 hosts) ===
        hosts = [
            ("mypoint-message1m", "192.168.10.101", "Message queue processor", "critical"),
            ("mypoint-message2m", "192.168.10.102", "Message queue processor (standby)", "high"),
            ("mypoint-monitor", "192.168.10.211", "Monitoring server (Prometheus+Alertmanager)", "high"),
            ("mypoint-db1", "192.168.10.50", "PostgreSQL primary", "critical"),
            ("mypoint-db2", "192.168.10.51", "PostgreSQL replica", "high"),
            ("mypoint-cache1", "192.168.10.60", "Redis cache primary", "high"),
            ("mypoint-cache2", "192.168.10.61", "Redis cache replica", "medium"),
            ("mypoint-api1", "192.168.10.30", "API gateway 1", "critical"),
            ("mypoint-api2", "192.168.10.31", "API gateway 2", "critical"),
            ("mypoint-worker1", "192.168.10.70", "Background worker", "medium"),
        ]
        for hostname, ip, role, crit in hosts:
            db.add(SystemInfo(
                id=uuid.uuid4(), hostname=hostname, ip_addresses=[ip],
                role=role, environment="prod", criticality=crit,
                owner="ops-team", escalation_contact="oncall@example.com",
                dependencies={"upstream": ["mypoint-api1"], "downstream": ["mypoint-db1"]} if "message" in hostname else {},
            ))

        # === INCIDENTS (3) ===
        now = datetime.now(timezone.utc)
        inc1_id = uuid.uuid4()
        inc2_id = uuid.uuid4()
        inc3_id = uuid.uuid4()

        db.add(Incident(
            id=inc1_id, title="[HighCPU] CPU usage is above 90%",
            severity="critical", status="investigating", source="alertmanager",
            fingerprint="abc123def456", impacted_service="message-queue",
            impacted_host="mypoint-message1m",
            raw_payload={"alertname": "HighCPU", "severity": "critical", "instance": "mypoint-message1m:9100"},
            normalized_event={"alertname": "HighCPU", "host": "mypoint-message1m", "severity": "critical"},
            created_at=now - timedelta(hours=2),
        ))
        db.add(Incident(
            id=inc2_id, title="[DiskUsageHigh] Disk usage above 85%",
            severity="warning", status="acknowledged", source="alertmanager",
            fingerprint="disk87monitor", impacted_host="mypoint-monitor",
            normalized_event={"alertname": "DiskUsageHigh", "host": "mypoint-monitor"},
            created_at=now - timedelta(hours=1),
        ))
        db.add(Incident(
            id=inc3_id, title="[PostgreSQLSlowQuery] Slow query detected",
            severity="high", status="resolved", source="alertmanager",
            fingerprint="slowquery_db1", impacted_service="postgresql",
            impacted_host="mypoint-db1",
            normalized_event={"alertname": "PostgreSQLSlowQuery", "host": "mypoint-db1"},
            created_at=now - timedelta(days=1),
        ))

        # === RCA RESULTS ===
        db.add(RCAResult(
            id=uuid.uuid4(), incident_id=inc1_id, round_number=1,
            executive_summary="CPU spike tren mypoint-message1m. Can thu thap process list de xac dinh.",
            probable_cause="Unknown - chua du evidence",
            confidence=0.35, missing_context=["process list", "application logs"],
            next_checks=["get_top_cpu_processes", "tail_log"],
        ))
        db.add(RCAResult(
            id=uuid.uuid4(), incident_id=inc3_id, round_number=1,
            executive_summary="Slow query tren mypoint-db1. Kiem tra query plan.",
            probable_cause="Unindexed query tu batch job analytics_export",
            confidence=0.82, missing_context=[],
            next_checks=["Kiem tra index", "Review batch job schedule"],
        ))

        # === ADR ===
        db.add(ArchitectureDecision(
            id=uuid.uuid4(), title="ADR-001: Split-plane architecture",
            context="Private zone khong cho phep inbound connection tu Internet",
            decision="Su dung split-plane: public control plane + private production zone",
            rationale="Giam exposure, private agent chi goi outbound den public",
            consequences="Can poll-based communication, khong real-time push",
            status="active", component="platform", created_by="admin",
        ))

        # === KNOWLEDGE BASE ===
        db.add(KnowledgeBase(
            id=uuid.uuid4(), type="known_issue",
            title="analytics_export batch job thieu CPU limit",
            content="Batch job analytics_export khong co CPU limit, da ghi nhan 3 lan spike. Workaround: kill process manually. Fix: add CPU cgroup limit.",
            tags=["cpu", "batch-job"], linked_services=["message-queue"],
            severity="high", status="active", created_by="admin",
        ))
        db.add(KnowledgeBase(
            id=uuid.uuid4(), type="runbook",
            title="High CPU troubleshooting",
            content="1. Check top processes: top -bn1\
2. Check service logs\
3. If batch job: check cron schedule\
4. If application: check thread pool",
            tags=["cpu", "troubleshooting"], linked_alert_names=["HighCPU"],
            status="active", created_by="admin",
        ))

        await db.commit()
        print("[SEED] Demo data loaded successfully!")
        print("[SEED] Users: admin/admin123, operator/operator123, viewer/viewer123")


if __name__ == "__main__":
    asyncio.run(seed())
