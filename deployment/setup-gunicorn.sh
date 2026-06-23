#!/bin/bash

# Gunicorn + Django WSGI kurulumu ve systemd service güncelleme
# Production: portfolio.wsgi:application via run_gunicorn.py

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=config.sh
source "$SCRIPT_DIR/config.sh"

echo "=== Django Gunicorn Kurulumu ==="
echo ""

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

VENV_DIR="$PROJECT_DIR/backend/venv"
SERVICE_FILE="/etc/systemd/system/cankartal-backend.service"
ENV_FILE="$PROJECT_DIR/backend/.env"

if [ ! -d "$VENV_DIR" ]; then
    echo -e "${RED}Virtual environment bulunamadı: $VENV_DIR${NC}"
    echo "Önce: ./install-dependencies.sh"
    exit 1
fi

source "$VENV_DIR/bin/activate"

echo -e "${YELLOW}Bağımlılıklar kontrol ediliyor...${NC}"
cd "$PROJECT_DIR/backend"
pip install -r requirements.txt
echo -e "${GREEN}Bağımlılıklar hazır.${NC}"

echo -e "${YELLOW}Django production ayarları kontrol ediliyor...${NC}"
export DJANGO_SETTINGS_MODULE=portfolio.settings.prod
python manage.py check
echo -e "${GREEN}Django check OK.${NC}"

echo -e "${YELLOW}Upload dizinleri hazırlanıyor...${NC}"
UPLOAD_DIR="$PROJECT_DIR/backend/static/uploads"
PROFILES_DIR="$UPLOAD_DIR/profiles"
mkdir -p "$PROFILES_DIR"
chown -R ubuntu:ubuntu "$UPLOAD_DIR" 2>/dev/null || sudo chown -R ubuntu:ubuntu "$UPLOAD_DIR"
chmod -R 755 "$UPLOAD_DIR"
chmod -R 775 "$PROFILES_DIR"
echo -e "${GREEN}Upload dizinleri hazır.${NC}"

PROD_PORT=8000
if [ -f "$ENV_FILE" ] && grep -q "^prod_port=" "$ENV_FILE"; then
    PROD_PORT=$(grep "^prod_port=" "$ENV_FILE" | cut -d '=' -f2 | tr -d ' \r')
fi
echo -e "${GREEN}Production port (prod_port): $PROD_PORT${NC}"
echo -e "${YELLOW}Nginx proxy_pass bu port ile eşleşmeli!${NC}"

echo -e "${YELLOW}Systemd service dosyası güncelleniyor...${NC}"
sudo tee "$SERVICE_FILE" > /dev/null <<EOF
[Unit]
Description=Cankartal Portfolio Backend (Django REST API + Gunicorn)
After=network.target mysql.service

[Service]
Type=simple
User=ubuntu
Group=ubuntu
WorkingDirectory=$PROJECT_DIR/backend
Environment="PATH=$VENV_DIR/bin"
Environment="PYTHONUNBUFFERED=1"
Environment="DJANGO_SETTINGS_MODULE=portfolio.settings.prod"
EnvironmentFile=-$ENV_FILE
ExecStart=$VENV_DIR/bin/python $PROJECT_DIR/backend/run_gunicorn.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal
NoNewPrivileges=true
PrivateTmp=true

[Install]
WantedBy=multi-user.target
EOF

echo -e "${GREEN}Service dosyası güncellendi.${NC}"

sudo systemctl daemon-reload
sudo systemctl enable cankartal-backend
sudo systemctl restart cankartal-backend

sleep 2
if sudo systemctl is-active --quiet cankartal-backend; then
    echo -e "${GREEN}Service başarıyla başlatıldı (WSGI / port $PROD_PORT).${NC}"
    sudo systemctl status cankartal-backend --no-pager -l | head -20
else
    echo -e "${RED}HATA: Service başlatılamadı!${NC}"
    echo "sudo journalctl -u cankartal-backend -n 50"
    exit 1
fi

deactivate

echo ""
echo -e "${GREEN}=== Gunicorn (Django WSGI) Kurulumu Tamamlandı ===${NC}"
echo "WSGI entry: portfolio.wsgi:application"
echo "Health:     curl http://127.0.0.1:${PROD_PORT}/api/v1/health"
