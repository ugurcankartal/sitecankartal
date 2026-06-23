#!/bin/bash

# API test script (Django REST API)

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=config.sh
source "$SCRIPT_DIR/config.sh"

ENV_FILE="$PROJECT_DIR/backend/.env"

PROD_PORT=8000
if [ -f "$ENV_FILE" ] && grep -q "^prod_port=" "$ENV_FILE"; then
    PROD_PORT=$(grep "^prod_port=" "$ENV_FILE" | cut -d '=' -f2 | tr -d ' \r')
fi

echo "=== API Test (Django DRF) ==="
echo "Production port (prod_port): $PROD_PORT"
echo ""

echo "1. Health check (localhost:${PROD_PORT}):"
curl -s "http://127.0.0.1:${PROD_PORT}/api/v1/health"
echo ""
echo ""

echo "2. Blog API (localhost:${PROD_PORT}):"
curl -s "http://127.0.0.1:${PROD_PORT}/api/v1/blog?per_page=5" | head -20
echo ""
echo ""

echo "3. Nginx üzerinden test (HTTPS):"
curl -s "https://cankartal.com/api/v1/health"
echo ""
echo ""

echo "4. Blog via Nginx:"
curl -s "https://cankartal.com/api/v1/blog?per_page=5" | head -20
echo ""
