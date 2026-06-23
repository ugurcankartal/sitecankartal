#!/bin/bash

# Upload dizini izinlerini düzeltme scripti
# Backend servisinin dosya yüklemesi için gerekli izinleri ayarlar

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=config.sh
source "$SCRIPT_DIR/config.sh"

echo "=== Upload Dizin İzinlerini Düzeltme ==="
echo ""

# Renkler
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

UPLOAD_DIR="$PROJECT_DIR/backend/static/uploads"
PROFILES_DIR="$UPLOAD_DIR/profiles"

# Dizinleri oluştur
echo -e "${YELLOW}Upload dizinleri oluşturuluyor...${NC}"
sudo mkdir -p "$PROFILES_DIR"
echo -e "${GREEN}Dizinler oluşturuldu.${NC}"

# Sahiplik ve izinleri ayarla
echo -e "${YELLOW}İzinler ayarlanıyor...${NC}"
sudo chown -R ubuntu:ubuntu "$UPLOAD_DIR"
sudo chmod -R 755 "$UPLOAD_DIR"
sudo chmod -R 775 "$PROFILES_DIR"  # Yazma izni için
echo -e "${GREEN}İzinler ayarlandı.${NC}"

# Mevcut dosyaların izinlerini de düzelt
if [ -d "$PROFILES_DIR" ]; then
    echo -e "${YELLOW}Mevcut dosyaların izinleri düzeltiliyor...${NC}"
    sudo chown -R ubuntu:ubuntu "$PROFILES_DIR"/* 2>/dev/null || true
    sudo chmod -R 644 "$PROFILES_DIR"/* 2>/dev/null || true
    echo -e "${GREEN}Dosya izinleri düzeltildi.${NC}"
fi

# Test: ubuntu kullanıcısı olarak yazma testi
echo -e "${YELLOW}Yazma izni test ediliyor...${NC}"
sudo -u ubuntu touch "$PROFILES_DIR/.write_test" 2>/dev/null && sudo -u ubuntu rm "$PROFILES_DIR/.write_test" && echo -e "${GREEN}✓ Yazma izni OK${NC}" || echo -e "${RED}✗ Yazma izni HATALI${NC}"

echo ""
echo -e "${GREEN}=== İzin Düzeltme Tamamlandı ===${NC}"
echo ""
echo "Dizin: $PROFILES_DIR"
echo "Sahip: ubuntu:ubuntu"
echo "İzinler: 775 (rwxrwxr-x)"
echo ""
echo "Backend servisini yeniden başlatın:"
echo "  sudo systemctl restart cankartal-backend"
