"""auth.py - HMAC authentication cho private agent"""
import hmac
import hashlib
import time
import uuid
from config import AGENT_ID, AGENT_SECRET


def get_auth_headers() -> dict:
    """Tao HMAC headers cho moi request gui len public"""
    timestamp = str(int(time.time()))
    nonce = str(uuid.uuid4())
    message = f"{AGENT_ID}{timestamp}{nonce}"
    signature = hmac.new(
        AGENT_SECRET.encode(), message.encode(), hashlib.sha256
    ).hexdigest()

    return {
        "X-Agent-ID": AGENT_ID,
        "X-Timestamp": timestamp,
        "X-Nonce": nonce,
        "X-Signature": signature,
    }
