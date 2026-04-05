#!/bin/bash
echo "=== Health Check ==="
echo ""
echo "--- Docker Containers ---"
docker compose ps
echo ""
echo "--- API Health ---"
curl -s http://localhost:8000/api/v1/health | python3 -m json.tool 2>/dev/null || echo "Backend: NOT REACHABLE"
echo ""
echo "--- Database ---"
docker compose exec -T postgres pg_isready -U aiops && echo "PostgreSQL: OK" || echo "PostgreSQL: FAILED"
echo ""
echo "--- Redis ---"
docker compose exec -T redis redis-cli ping && echo "Redis: OK" || echo "Redis: FAILED"
