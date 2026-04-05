#!/usr/bin/env python3
"""
agent.py - Entry point cua Private Diagnostic Agent
Chay: python agent.py
Hoac: systemctl start private_agent
"""
import time
import threading
from config import AGENT_ID, PUBLIC_URL, POLL_INTERVAL, HEARTBEAT_INTERVAL, INVENTORY_INTERVAL
from poll import poll_tasks, send_heartbeat, sync_inventory


def main():
    print(f"[AGENT] Starting: {AGENT_ID}")
    print(f"[AGENT] Public URL: {PUBLIC_URL}")
    print(f"[AGENT] Poll: {POLL_INTERVAL}s | Heartbeat: {HEARTBEAT_INTERVAL}s | Inventory: {INVENTORY_INTERVAL}s")

    last_heartbeat = 0
    last_inventory = 0
    last_poll = 0

    while True:
        now = time.time()

        # Heartbeat
        if now - last_heartbeat >= HEARTBEAT_INTERVAL:
            send_heartbeat()
            last_heartbeat = now

        # Inventory sync
        if now - last_inventory >= INVENTORY_INTERVAL:
            sync_inventory()
            last_inventory = now

        # Poll tasks
        if now - last_poll >= POLL_INTERVAL:
            poll_tasks()
            last_poll = now

        time.sleep(1)


if __name__ == "__main__":
    main()
