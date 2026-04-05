"""poll.py - Poll task, heartbeat, inventory sync"""
import time
import socket
import json
from datetime import datetime, timezone
import httpx
from config import AGENT_ID, PUBLIC_URL, POLL_INTERVAL, HEARTBEAT_INTERVAL, INVENTORY_INTERVAL
from auth import get_auth_headers
from tools.executor import execute_tool


def poll_tasks():
    """Poll task tu public server"""
    try:
        headers = get_auth_headers()
        r = httpx.get(f"{PUBLIC_URL}/api/v1/agent/tasks", headers=headers, timeout=10, verify=False)
        if r.status_code == 200:
            data = r.json()
            tasks = data.get("tasks", [])
            for task in tasks:
                print(f"[TASK] Executing: {task['tool_name']}")
                result = execute_tool(task["tool_name"], task.get("tool_input", {}))

                # Gui ket qua
                payload = {
                    "task_id": task["task_id"],
                    "agent_id": AGENT_ID,
                    "tool_name": task["tool_name"],
                    "status": result["status"],
                    "output": result["output"],
                    "executed_at": datetime.now(timezone.utc).isoformat(),
                    "duration_ms": result["duration_ms"],
                }
                headers2 = get_auth_headers()
                headers2["Content-Type"] = "application/json"
                r2 = httpx.post(f"{PUBLIC_URL}/api/v1/agent/results",
                               headers=headers2, json=payload, timeout=10, verify=False)
                print(f"[TASK] Result sent: {r2.status_code}")
    except Exception as e:
        print(f"[ERROR] Poll failed: {e}")


def send_heartbeat():
    """Gui heartbeat"""
    try:
        headers = get_auth_headers()
        headers["Content-Type"] = "application/json"
        payload = {
            "agent_id": AGENT_ID,
            "hostname": socket.gethostname(),
            "version": "1.0.0",
            "status": "healthy",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        r = httpx.post(f"{PUBLIC_URL}/api/v1/agent/heartbeat",
                      headers=headers, json=payload, timeout=10, verify=False)
        if r.status_code == 200:
            print("[HEARTBEAT] OK")
        else:
            print(f"[HEARTBEAT] Failed: {r.status_code}")
    except Exception as e:
        print(f"[HEARTBEAT] Error: {e}")


def sync_inventory():
    """Dong bo inventory"""
    try:
        from tools.diagnostic import get_ip_addr, get_disk_usage, get_memory_usage, get_top_cpu_processes, get_listening_ports
        headers = get_auth_headers()
        headers["Content-Type"] = "application/json"
        payload = {
            "agent_id": AGENT_ID,
            "hostname": socket.gethostname(),
            "snapshot": {
                "os": "",
                "ip_addresses": [],
                "running_services": [],
                "listening_ports": [],
                "disk_usage": [],
                "memory_usage_pct": 0.0,
                "top_cpu_processes": [],
                "collected_at": datetime.now(timezone.utc).isoformat(),
            },
        }
        r = httpx.post(f"{PUBLIC_URL}/api/v1/agent/inventory",
                      headers=headers, json=payload, timeout=15, verify=False)
        print(f"[INVENTORY] Sync: {r.status_code}")
    except Exception as e:
        print(f"[INVENTORY] Error: {e}")
