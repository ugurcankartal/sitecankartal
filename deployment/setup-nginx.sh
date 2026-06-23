#!/bin/bash

# Nginx ve SSL kurulum scripti
# Ubuntu sunucusu için cankartal.com domain'i

set -e

echo "=== Nginx ve SSL Kurulum Scripti ==="
echo "Domain: cankartal.com"
echo ""

# Renkler
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 1. Nginx kurulumu
echo -e "${YELLOW}[1/6] Nginx kurulumu kontrol ediliyor...${NC}"
if ! command -v nginx &> /dev/null; then
    echo "Nginx kuruluyor..."
    sudo apt update
    sudo apt install -y nginx
else
    echo -e "${GREEN}Nginx zaten kurulu.${NC}"
fi

# 2. Certbot kurulumu
echo -e "${YELLOW}[2/6] Certbot kurulumu kontrol ediliyor...${NC}"
if ! command -v certbot &> /dev/null; then
    echo "Certbot kuruluyor..."
    sudo apt install -y certbot python3-certbot-nginx
else
    echo -e "${GREEN}Certbot zaten kurulu.${NC}"
fi

# 3. Nginx konfigürasyon dosyasını kopyalama
echo -e "${YELLOW}[3/6] Nginx konfigürasyon dosyası kopyalanıyor...${NC}"
PROJECT_DIR="/home/ubuntu/projectcankartal"
NGINX_CONF="$PROJECT_DIR/nginx/cankartal.com.conf"
NGINX_SITES="/etc/nginx/sites-available"
NGINX_ENABLED="/etc/nginx/sites-enabled"

if [ -f "$NGINX_CONF" ]; then
    sudo cp "$NGINX_CONF" "$NGINX_SITES/cankartal.com"
    echo -e "${GREEN}Konfigürasyon dosyası kopyalandı.${NC}"
    
    # Frontend dist klasörünün varlığını kontrol et
    if [ ! -d "$PROJECT_DIR/Frontend/dist" ]; then
        echo -e "${YELLOW}UYARI: Frontend dist klasörü bulunamadı!${NC}"
        echo "Frontend build alınmalı: cd Frontend && npm run build"
    fi
else
    echo -e "${RED}HATA: Nginx konfigürasyon dosyası bulunamadı: $NGINX_CONF${NC}"
    exit 1
fi

# 4. Default site'ı devre dışı bırakma
echo -e "${YELLOW}[4/6] Default Nginx site devre dışı bırakılıyor...${NC}"
if [ -L "$NGINX_ENABLED/default" ]; then
    sudo rm "$NGINX_ENABLED/default"
    echo -e "${GREEN}Default site devre dışı bırakıldı.${NC}"
fi

# 5. Yeni site'ı aktif etme
echo -e "${YELLOW}[5/6] Yeni site aktif ediliyor...${NC}"
if [ ! -L "$NGINX_ENABLED/cankartal.com" ]; then
    sudo ln -s "$NGINX_SITES/cankartal.com" "$NGINX_ENABLED/cankartal.com"
    echo -e "${GREEN}Site aktif edildi.${NC}"
fi

# 6. Nginx konfigürasyon testi
echo -e "${YELLOW}[6/6] Nginx konfigürasyonu test ediliyor...${NC}"
if sudo nginx -t; then
    echo -e "${GREEN}Nginx konfigürasyonu geçerli.${NC}"
else
    echo -e "${RED}HATA: Nginx konfigürasyonu geçersiz!${NC}"
    exit 1
fi

# 7. Certbot directory oluşturma
echo -e "${YELLOW}[7/7] Certbot directory oluşturuluyor...${NC}"
sudo mkdir -p /var/www/certbot
sudo chown -R www-data:www-data /var/www/certbot

echo ""
echo -e "${GREEN}=== Kurulum Tamamlandı ===${NC}"
echo ""
echo "Sonraki adımlar:"
echo "1. DNS kayıtlarınızı kontrol edin (A record: sunucu IP adresi)"
echo "2. SSL sertifikası almak için şu komutu çalıştırın:"
echo "   sudo certbot --nginx -d cankartal.com -d www.cankartal.com"
echo "3. Nginx'i yeniden başlatın:"
echo "   sudo systemctl restart nginx"
echo "4. Nginx durumunu kontrol edin:"
echo "   sudo systemctl status nginx"
