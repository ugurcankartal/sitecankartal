#!/bin/bash

# SSL sertifikası kurulum scripti
# Let's Encrypt ile cankartal.com için SSL

set -e

echo "=== SSL Sertifikası Kurulum Scripti ==="
echo "Domain: cankartal.com"
echo ""

# Renkler
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Domain kontrolü
DOMAIN="cankartal.com"
WWW_DOMAIN="www.cankartal.com"

echo -e "${YELLOW}SSL sertifikası alınıyor...${NC}"
echo "Domain: $DOMAIN ve $WWW_DOMAIN"
echo ""

# Certbot ile SSL sertifikası alma
sudo certbot --nginx \
    -d $DOMAIN \
    -d $WWW_DOMAIN \
    --non-interactive \
    --agree-tos \
    --email admin@cankartal.com \
    --redirect

if [ $? -eq 0 ]; then
    echo ""
    echo -e "${GREEN}=== SSL Sertifikası Başarıyla Kuruldu ===${NC}"
    echo ""
    echo "Sertifika bilgileri:"
    sudo certbot certificates
    echo ""
    echo "Otomatik yenileme testi:"
    echo "sudo certbot renew --dry-run"
else
    echo -e "${RED}HATA: SSL sertifikası alınamadı!${NC}"
    echo ""
    echo "Kontrol edin:"
    echo "1. DNS kayıtlarının doğru olduğundan emin olun"
    echo "2. Port 80 ve 443'ün açık olduğundan emin olun"
    echo "3. Firewall ayarlarını kontrol edin"
    exit 1
fi

# Otomatik yenileme cron job kontrolü
echo -e "${YELLOW}Otomatik yenileme cron job kontrol ediliyor...${NC}"
if ! sudo crontab -l 2>/dev/null | grep -q "certbot renew"; then
    echo "Otomatik yenileme cron job ekleniyor..."
    (sudo crontab -l 2>/dev/null; echo "0 0,12 * * * certbot renew --quiet --post-hook 'systemctl reload nginx'") | sudo crontab -
    echo -e "${GREEN}Otomatik yenileme cron job eklendi.${NC}"
else
    echo -e "${GREEN}Otomatik yenileme cron job zaten mevcut.${NC}"
fi

echo ""
echo -e "${GREEN}=== SSL Kurulumu Tamamlandı ===${NC}"
