#!/bin/bash

# Systemd service dosyası oluşturma scripti
# Django backend için systemd service (Gunicorn)

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=config.sh
source "$SCRIPT_DIR/config.sh"

echo "=== Systemd Service Kurulum Scripti ==="
echo ""

# Renkler
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

VENV_DIR="$PROJECT_DIR/backend/venv"
SERVICE_NAME="cankartal-backend"
SERVICE_FILE="/etc/systemd/system/${SERVICE_NAME}.service"

# Python ve virtual environment kontrolü
echo -e "${YELLOW}[1/4] Python ve virtual environment kontrol ediliyor...${NC}"
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}HATA: Python3 bulunamadı!${NC}"
    exit 1
fi

# Virtual environment oluşturma (yoksa)
VENV_DIR="$PROJECT_DIR/backend/venv"
if [ ! -d "$VENV_DIR" ]; then
    echo "Virtual environment oluşturuluyor..."
    cd "$PROJECT_DIR/backend"
    python3 -m venv venv
    echo -e "${GREEN}Virtual environment oluşturuldu.${NC}"
fi

# Bağımlılıkları yükle
echo "Bağımlılıklar yükleniyor..."
cd "$PROJECT_DIR/backend"
source "$VENV_DIR/bin/activate"
pip install --upgrade pip
pip install -r requirements.txt
echo -e "${GREEN}Bağımlılıklar yüklendi.${NC}"

# .env dosyası kontrolü
if [ ! -f "$PROJECT_DIR/backend/.env" ]; then
    echo -e "${YELLOW}UYARI: .env dosyası bulunamadı!${NC}"
    echo "Lütfen $PROJECT_DIR/backend/.env dosyasını oluşturun."
    echo "Örnek içerik için deployment/README.md dosyasına bakın."
fi

ENV_FILE="$PROJECT_DIR/backend/.env"

PROD_PORT=8000
if [ -f "$ENV_FILE" ] && grep -q "^prod_port=" "$ENV_FILE"; then
    PROD_PORT=$(grep "^prod_port=" "$ENV_FILE" | cut -d '=' -f2 | tr -d ' \r')
fi
echo -e "${GREEN}Production port (prod_port): $PROD_PORT${NC}"

# Systemd service dosyası oluşturma
echo -e "${YELLOW}[3/5] Systemd service dosyası oluşturuluyor...${NC}"

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
EnvironmentFile=-$PROJECT_DIR/backend/.env
Environment="DJANGO_SETTINGS_MODULE=portfolio.settings.prod"
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

echo -e "${GREEN}Service dosyası oluşturuldu.${NC}"

# Systemd reload
echo -e "${YELLOW}[4/5] Systemd reload ediliyor...${NC}"
sudo systemctl daemon-reload
echo -e "${GREEN}Systemd reload edildi.${NC}"

# Service'i aktif etme
echo -e "${YELLOW}[5/5] Service aktif ediliyor...${NC}"
sudo systemctl enable $SERVICE_NAME
sudo systemctl start $SERVICE_NAME

# Durum kontrolü
sleep 2
if sudo systemctl is-active --quiet $SERVICE_NAME; then
    echo -e "${GREEN}Service başarıyla başlatıldı.${NC}"
else
    echo -e "${RED}HATA: Service başlatılamadı!${NC}"
    echo "Logları kontrol edin:"
    echo "sudo journalctl -u $SERVICE_NAME -n 50"
    exit 1
fi

echo ""
echo -e "${GREEN}=== Systemd Service Kurulumu Tamamlandı ===${NC}"
echo ""
echo "Kullanışlı komutlar:"
echo "  Service durumu:     sudo systemctl status $SERVICE_NAME"
echo "  Service başlat:     sudo systemctl start $SERVICE_NAME"
echo "  Service durdur:     sudo systemctl stop $SERVICE_NAME"
echo "  Service yeniden:    sudo systemctl restart $SERVICE_NAME"
echo "  Logları görüntüle:  sudo journalctl -u $SERVICE_NAME -f"
