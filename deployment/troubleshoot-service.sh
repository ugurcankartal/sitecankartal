#!/bin/bash

# Systemd service sorun giderme scripti

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=config.sh
source "$SCRIPT_DIR/config.sh"

SERVICE_NAME="cankartal-backend"
VENV_DIR="$PROJECT_DIR/backend/venv"
ENV_FILE="$PROJECT_DIR/backend/.env"

PROD_PORT=8000
if [ -f "$ENV_FILE" ] && grep -q "^prod_port=" "$ENV_FILE"; then
    PROD_PORT=$(grep "^prod_port=" "$ENV_FILE" | cut -d '=' -f2 | tr -d ' \r')
fi

echo "=== Systemd Service Sorun Giderme ==="
echo ""

# Renkler
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# 1. Service durumu
echo "1. Service durumu:"
sudo systemctl status $SERVICE_NAME --no-pager -l || true
echo ""

# 2. Son 50 log satırı
echo "2. Son 50 log satırı:"
sudo journalctl -u $SERVICE_NAME -n 50 --no-pager || true
echo ""

# 3. Virtual environment kontrolü
echo "3. Virtual environment kontrolü:"
if [ -d "$VENV_DIR" ]; then
    echo -e "${GREEN}Virtual environment mevcut: $VENV_DIR${NC}"
    if [ -f "$VENV_DIR/bin/python" ]; then
        echo -e "${GREEN}Python executable mevcut${NC}"
        echo "Python versiyonu:"
        $VENV_DIR/bin/python --version
    else
        echo -e "${RED}Python executable bulunamadı!${NC}"
    fi
else
    echo -e "${RED}Virtual environment bulunamadı: $VENV_DIR${NC}"
fi
echo ""

# 4. Bağımlılık kontrolü
echo "4. Bağımlılık kontrolü:"
if [ -d "$VENV_DIR" ]; then
    echo "Django kontrolü:"
    $VENV_DIR/bin/pip show django 2>/dev/null || echo -e "${RED}Django yüklü değil!${NC}"
    echo ""
    echo "Tüm bağımlılıklar:"
    $VENV_DIR/bin/pip list || true
fi
echo ""

# 5. .env dosyası kontrolü
echo "5. .env dosyası kontrolü:"
if [ -f "$PROJECT_DIR/backend/.env" ]; then
    echo -e "${GREEN}.env dosyası mevcut${NC}"
    echo "Dosya boyutu: $(wc -l < $PROJECT_DIR/backend/.env) satır"
    echo "İçerik (gizli):"
    grep -v "PASSWORD\|SECRET\|KEY" "$PROJECT_DIR/backend/.env" || true
else
    echo -e "${RED}.env dosyası bulunamadı!${NC}"
fi
echo ""

# 6. Manuel test
echo "6. Manuel test (Python import):"
cd "$PROJECT_DIR/backend"
if [ -d "$VENV_DIR" ]; then
    source "$VENV_DIR/bin/activate"
    echo "Python path testi:"
    python -c "import sys; print('Python:', sys.executable)" || echo -e "${RED}Python çalışmıyor!${NC}"
    echo ""
    echo "Django import testi:"
    python -c "import django; print('Django OK')" || echo -e "${RED}Django import edilemiyor!${NC}"
    echo ""
    echo "WSGI import testi:"
    python -c "import os; os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'portfolio.settings.prod'); import portfolio.wsgi; print('WSGI OK')" || echo -e "${RED}WSGI import edilemiyor!${NC}"
    deactivate
fi
echo ""

# 7. Port kontrolü
echo "7. Port $PROD_PORT kontrolü (prod_port):"
if sudo lsof -i :$PROD_PORT 2>/dev/null; then
    echo -e "${YELLOW}Port $PROD_PORT kullanımda!${NC}"
else
    echo -e "${GREEN}Port $PROD_PORT boş${NC}"
fi
echo ""

# 8. Dosya izinleri
echo "8. Dosya izinleri:"
ls -la "$PROJECT_DIR/backend/manage.py" || echo -e "${RED}manage.py bulunamadı!${NC}"
ls -la "$VENV_DIR/bin/python" 2>/dev/null || echo -e "${RED}Python executable bulunamadı!${NC}"
echo ""

echo "=== Sorun Giderme Tamamlandı ==="
echo ""
echo "Öneriler:"
echo "1. Eğer bağımlılıklar eksikse:"
echo "   cd $PROJECT_DIR/backend"
echo "   source venv/bin/activate"
echo "   pip install -r requirements.txt"
echo ""
echo "2. Eğer .env eksikse, oluşturun:"
echo "   nano $PROJECT_DIR/backend/.env"
echo ""
echo "3. Service'i yeniden başlatın:"
echo "   sudo systemctl restart $SERVICE_NAME"
echo "   sudo systemctl status $SERVICE_NAME"
