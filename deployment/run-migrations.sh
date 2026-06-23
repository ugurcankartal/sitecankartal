#!/bin/bash

# Django database migrations

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=config.sh
source "$SCRIPT_DIR/config.sh"

VENV_DIR="$PROJECT_DIR/backend/venv"
ENV_FILE="$PROJECT_DIR/backend/.env"

echo "=== Django Migrations ==="
echo ""

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

if [ ! -f "$ENV_FILE" ]; then
    echo -e "${RED}.env dosyası bulunamadı: $ENV_FILE${NC}"
    exit 1
fi

cd "$PROJECT_DIR/backend"
source "$VENV_DIR/bin/activate"

export DJANGO_SETTINGS_MODULE=portfolio.settings.prod

echo -e "${YELLOW}Django check...${NC}"
python manage.py check

echo -e "${YELLOW}Migrations uygulanıyor...${NC}"
python manage.py migrate --fake-initial

deactivate

echo ""
echo -e "${GREEN}=== Migration Tamamlandı ===${NC}"
echo ""
echo "Backend service'i yeniden başlatın:"
echo "  sudo systemctl restart cankartal-backend"
