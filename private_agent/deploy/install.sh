#!/bin/bash
# Script cai dat private agent
set -e

echo "=== Cai dat Private Diagnostic Agent ==="

# Tao thu muc
sudo mkdir -p /opt/private-agent
sudo cp -r . /opt/private-agent/
cd /opt/private-agent

# Tao venv
python3.11 -m venv venv || python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Copy env
if [ ! -f .env ]; then
    cp .env.example .env
    echo "[WARN] Hay sua file /opt/private-agent/.env truoc khi chay!"
fi

# Cai systemd service
sudo cp deploy/private_agent.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable private_agent

echo "=== Cai dat xong! ==="
echo "1. Sua file /opt/private-agent/.env"
echo "2. sudo systemctl start private_agent"
echo "3. sudo systemctl status private_agent"
