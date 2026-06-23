#!/bin/bash

# Final test script for production deployment

echo "=== Production Deployment Test ==="
echo ""

# Renkler
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${YELLOW}1. Health API (HTTPS):${NC}"
RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" "https://cankartal.com/api/v1/health")
if [ "$RESPONSE" = "200" ]; then
    echo -e "${GREEN}✓ Health API çalışıyor (HTTP $RESPONSE)${NC}"
else
    echo -e "${RED}✗ Health API hatası (HTTP $RESPONSE)${NC}"
fi
echo ""

echo -e "${YELLOW}2. Blog API (HTTPS):${NC}"
RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" "https://cankartal.com/api/v1/blog?per_page=100")
if [ "$RESPONSE" = "200" ]; then
    echo -e "${GREEN}✓ API çalışıyor (HTTP $RESPONSE)${NC}"
else
    echo -e "${RED}✗ API hatası (HTTP $RESPONSE)${NC}"
fi
echo ""

echo -e "${YELLOW}3. Static File Test:${NC}"
RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" "https://cankartal.com/static/uploads/profiles/20260218145455_WhatsApp_Image_2025-12-18_at_17.33.12.jpeg")
if [ "$RESPONSE" = "200" ]; then
    echo -e "${GREEN}✓ Static dosyalar çalışıyor (HTTP $RESPONSE)${NC}"
else
    echo -e "${RED}✗ Static dosya hatası (HTTP $RESPONSE)${NC}"
fi
echo ""

echo -e "${YELLOW}4. Frontend Test:${NC}"
RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" "https://cankartal.com/")
if [ "$RESPONSE" = "200" ]; then
    echo -e "${GREEN}✓ Frontend çalışıyor (HTTP $RESPONSE)${NC}"
else
    echo -e "${RED}✗ Frontend hatası (HTTP $RESPONSE)${NC}"
fi
echo ""

echo -e "${YELLOW}5. Backend Service Status:${NC}"
if sudo systemctl is-active --quiet cankartal-backend; then
    echo -e "${GREEN}✓ Backend service çalışıyor${NC}"
else
    echo -e "${RED}✗ Backend service çalışmıyor${NC}"
fi
echo ""

echo -e "${YELLOW}6. Nginx Status:${NC}"
if sudo systemctl is-active --quiet nginx; then
    echo -e "${GREEN}✓ Nginx çalışıyor${NC}"
else
    echo -e "${RED}✗ Nginx çalışmıyor${NC}"
fi
echo ""

echo "=== Test Tamamlandı ==="
