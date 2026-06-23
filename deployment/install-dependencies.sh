#!/bin/bash

# Backend bağımlılıklarını yükleme scripti

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=config.sh
source "$SCRIPT_DIR/config.sh"

VENV_DIR="$PROJECT_DIR/backend/venv"

echo "=== Backend Bağımlılıkları Yükleniyor ==="
echo ""

# Renkler
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Virtual environment kontrolü
if [ ! -d "$VENV_DIR" ]; then
    echo -e "${YELLOW}Virtual environment oluşturuluyor...${NC}"
    cd "$PROJECT_DIR/backend"
    python3 -m venv venv
    echo -e "${GREEN}Virtual environment oluşturuldu.${NC}"
fi

# Virtual environment'ı aktif et
echo -e "${YELLOW}Virtual environment aktif ediliyor...${NC}"
source "$VENV_DIR/bin/activate"

# Pip'i güncelle
echo -e "${YELLOW}Pip güncelleniyor...${NC}"
pip install --upgrade pip

# Bağımlılıkları yükle
echo -e "${YELLOW}Bağımlılıklar yükleniyor...${NC}"
cd "$PROJECT_DIR/backend"
pip install -r requirements.txt

# Yüklenen paketleri göster
echo ""
echo -e "${GREEN}=== Bağımlılıklar Yüklendi ===${NC}"
echo ""
echo "Yüklenen paketler:"
pip list

# Test
echo ""
echo -e "${YELLOW}Test ediliyor...${NC}"
export DJANGO_SETTINGS_MODULE=portfolio.settings.prod
python -c "import django; print('✓ Django OK')" && echo -e "${GREEN}Django başarıyla import edildi!${NC}" || echo -e "${RED}Django import hatası!${NC}"
python -c "import portfolio.wsgi; import django; django.setup(); from django.conf import settings; assert settings.SETTINGS_MODULE == 'portfolio.settings.prod'; print('✓ WSGI OK (prod)')" && echo -e "${GREEN}WSGI entry point OK!${NC}" || echo -e "${RED}WSGI import hatası!${NC}"
python manage.py check && echo -e "${GREEN}manage.py check OK!${NC}" || echo -e "${RED}manage.py check hatası!${NC}"

deactivate

echo ""
echo -e "${GREEN}=== Kurulum Tamamlandı ===${NC}"
echo ""
echo "Service'i yeniden başlatın:"
echo "  sudo systemctl restart cankartal-backend"
echo "  sudo systemctl status cankartal-backend"
