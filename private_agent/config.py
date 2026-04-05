"""config.py - Cau hinh private agent"""
import os
from dotenv import load_dotenv
load_dotenv()

AGENT_ID = os.getenv("AGENT_ID", "agent-default")
AGENT_SECRET = os.getenv("AGENT_SECRET", "change-me")
PUBLIC_URL = os.getenv("PUBLIC_URL", "https://app.example.com")
POLL_INTERVAL = int(os.getenv("POLL_INTERVAL", "15"))
HEARTBEAT_INTERVAL = int(os.getenv("HEARTBEAT_INTERVAL", "30"))
INVENTORY_INTERVAL = int(os.getenv("INVENTORY_INTERVAL", "300"))
