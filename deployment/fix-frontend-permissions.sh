#!/bin/bash

# Frontend build izin sorunlarını düzeltme scripti

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=config.sh
source "$SCRIPT_DIR/config.sh"

FRONTEND_DIR="$PROJECT_DIR/Frontend"

echo "=== Frontend İzin Sorunları Düzeltiliyor ==="
echo ""

# Renkler
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

cd "$FRONTEND_DIR"

# node_modules/.bin dizinindeki dosyalara çalıştırılabilir izni ver
echo -e "${YELLOW}node_modules/.bin izinleri düzeltiliyor...${NC}"
if [ -d "node_modules/.bin" ]; then
    chmod +x node_modules/.bin/*
    echo -e "${GREEN}İzinler düzeltildi.${NC}"
else
    echo -e "${RED}node_modules/.bin dizini bulunamadı!${NC}"
    echo "npm install çalıştırılıyor..."
    npm install
    chmod +x node_modules/.bin/*
fi

# npm cache temizle (opsiyonel)
echo -e "${YELLOW}npm cache temizleniyor...${NC}"
npm cache clean --force 2>/dev/null || true

echo ""
echo -e "${GREEN}=== İzin Düzeltmeleri Tamamlandı ===${NC}"
echo ""
echo "Şimdi build almayı deneyin:"
echo "  npm run build"
echo ""
echo "Veya direkt npx kullanın:"
echo "  npx vite build"
