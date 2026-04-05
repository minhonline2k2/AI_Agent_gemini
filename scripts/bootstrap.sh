#!/bin/bash
# Bootstrap script - chay 1 lan khi setup lan dau
set -e

echo "=== AI Incident Platform Bootstrap ==="

# Kiem tra Docker
if ! command -v docker &> /dev/null; then
    echo "Docker chua cai. Dang cai..."
    curl -fsSL https://get.docker.com -o get-docker.sh
    sudo sh get-docker.sh
    rm get-docker.sh
fi

# Kiem tra .env
if [ ! -f .env ]; then
    echo "Tao file .env tu .env.example..."
    cp .env.example .env
    echo "[WARN] Hay sua file .env truoc khi tiep tuc!"
    exit 1
fi

# Tao thu muc SSL
mkdir -p nginx/ssl

# Build va chay
echo "Dang build va khoi dong..."
docker compose up -d --build

# Doi services khoi dong
echo "Doi services khoi dong (30s)..."
sleep 30

# Chay migration
echo "Chay database migration..."
docker compose exec backend alembic upgrade head 2>/dev/null || echo "Migration skipped (tables may already exist)"

# Seed data
echo "Nap du lieu demo..."
docker compose exec backend python -m seed.demo_data 2>/dev/null || echo "Seed skipped (data may already exist)"

echo ""
echo "=== HOAN THANH! ==="
echo "Truy cap: https://app.example.com"
echo "Login: admin / admin123"
