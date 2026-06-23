#!/bin/bash

# Frontend'i production için yeniden build etme scripti

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=config.sh
source "$SCRIPT_DIR/config.sh"

FRONTEND_DIR="$PROJECT_DIR/Frontend"

echo "=== Frontend Production Build ==="
echo ""

# Renkler
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

cd "$FRONTEND_DIR"

# Eski build'i temizle
if [ -d "dist" ]; then
    echo -e "${YELLOW}Eski build temizleniyor...${NC}"
    rm -rf dist
fi

# Production build
echo -e "${YELLOW}Production build alınıyor...${NC}"
npm run build

# İzinleri düzelt
echo -e "${YELLOW}İzinler düzeltiliyor...${NC}"
chmod -R 755 dist

echo ""
echo -e "${GREEN}=== Build Tamamlandı ===${NC}"
echo ""
echo "Build dosyaları: $FRONTEND_DIR/dist"
echo ""
echo "Nginx'i yeniden başlatın:"
echo "  sudo systemctl reload nginx"
