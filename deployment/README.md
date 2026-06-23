# Deployment Guide - cankartal.com

Bu rehber, cankartal.com projesini Ubuntu sunucusunda **Django REST API + Gunicorn (WSGI)** ile deploy etmek için adımları içerir.

> **Not:** Eski Flask backend `backend-flask/` klasöründedir. Production'da kullanılmaz.

## Gereksinimler

- Ubuntu 20.04 veya üzeri
- Root veya sudo yetkisi
- Domain DNS kayıtları (cankartal.com)
- Port 80 ve 443 açık

## Proje Yapısı

```
/home/ubuntu/sitecankartal/sitecankartal/
├── backend/          # Django REST API (production)
├── backend-flask/    # Legacy Flask (kullanılmıyor)
├── Frontend/         # React frontend
├── nginx/            # Nginx konfigürasyonları
└── deployment/       # Deployment scriptleri
```

Tüm deployment scriptleri `deployment/config.sh` içindeki `PROJECT_DIR` değerini kullanır. Sunucu yolu değişirse yalnızca bu dosyayı düzenleyin.

## Sunucuda İlk Kurulum

### 1. Sistem paketleri

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y python3 python3-pip python3-venv mysql-server nginx certbot python3-certbot-nginx
```

### 2. MySQL

```bash
sudo mysql
CREATE DATABASE IF NOT EXISTS personal_portfolio CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
EXIT;
```

### 3. Backend (Django)

```bash
cd /home/ubuntu/sitecankartal/sitecankartal/deployment
chmod +x *.sh
./install-dependencies.sh
```

`backend/.env` dosyasını oluşturun:

```env
dev_DJANGO_DEBUG=False
prod_DJANGO_DEBUG=False
prod_ALLOWED_HOSTS=cankartal.com,www.cankartal.com

# Development DB (local only)
dev_MYSQL_HOST=127.0.0.1
dev_MYSQL_PORT=3306
dev_MYSQL_USER=root
dev_MYSQL_PASSWORD=...
dev_MYSQL_DATABASE=personal_portfolio
dev_SECRET_KEY=...

# Production DB
prod_MYSQL_HOST=127.0.0.1
prod_MYSQL_PORT=3306
prod_MYSQL_USER=root
prod_MYSQL_PASSWORD=...
prod_MYSQL_DATABASE=personal_portfolio
prod_SECRET_KEY=...

BIND_HOST=127.0.0.1
dev_port=47800
prod_port=59254

SESSION_COOKIE_SECURE=True
CORS_ORIGINS=https://cankartal.com,https://www.cankartal.com
```

```bash
./run-migrations.sh
python manage.py create_superadmin   # backend/venv aktifken
```

### 4. Gunicorn + systemd (WSGI)

```bash
./setup-gunicorn.sh
# veya ilk kurulumda:
./setup-systemd.sh
```

Service şunları çalıştırır:
- `portfolio.wsgi:application`
- `run_gunicorn.py` → `prod_port` (.env)
- `DJANGO_SETTINGS_MODULE=portfolio.settings.prod`

### 5. Frontend build

```bash
cd /home/ubuntu/sitecankartal/sitecankartal/Frontend
npm install
npm run build
```

API base URL production'da `/api/v1` (nginx proxy).

```bash
./rebuild-frontend.sh
```

### 6. Nginx + SSL

```bash
./setup-nginx.sh
./setup-ssl.sh
```

`nginx/cankartal.com.conf` içindeki `proxy_pass` portu **prod_port** ile aynı olmalı (varsayılan: 59254).

### 7. Upload izinleri

```bash
./fix-upload-permissions.sh
```

## Flask'tan Django'ya Geçiş (mevcut sunucu)

```bash
# 1. Eski Flask servisini durdur
sudo systemctl stop cankartal-backend

# 2. Kodu güncelle (git pull / dosya kopyala)
cd /home/ubuntu/sitecankartal/sitecankartal

# 3. Django bağımlılıkları
./deployment/install-dependencies.sh

# 4. .env dosyasını yeni formata güncelle (dev_/prod_ MYSQL, prod_SECRET_KEY)

# 5. Migrations
./deployment/run-migrations.sh

# 6. Gunicorn WSGI service
./deployment/setup-gunicorn.sh

# 7. Nginx config güncelle ve reload
sudo cp nginx/cankartal.com.conf /etc/nginx/sites-available/cankartal.com
sudo nginx -t && sudo systemctl reload nginx

# 8. Test
./deployment/test-api.sh
./deployment/final-test.sh
```

## Servis Yönetimi

```bash
sudo systemctl status cankartal-backend
sudo systemctl restart cankartal-backend
sudo journalctl -u cankartal-backend -f
```

## API Endpoint'leri

| Endpoint | Açıklama |
|----------|----------|
| `GET /api/v1/health` | Health check |
| `GET /api/v1/profile` | Profil |
| `GET /api/v1/blog` | Blog |
| `/admin` | Admin panel |

## Sorun Giderme

```bash
./troubleshoot-service.sh
./test-api.sh
```

### Port kullanımda

```bash
# prod_port değerini .env'den kontrol edin
grep prod_port /home/ubuntu/sitecankartal/sitecankartal/backend/.env
sudo lsof -i :59254
```

### WSGI test

```bash
cd /home/ubuntu/sitecankartal/sitecankartal/backend
source venv/bin/activate
export DJANGO_SETTINGS_MODULE=portfolio.settings.prod
python manage.py check
python run_gunicorn.py
```

## Güncelleme

```bash
cd /home/ubuntu/sitecankartal/sitecankartal/backend
source venv/bin/activate
git pull
pip install -r requirements.txt
python manage.py migrate
sudo systemctl restart cankartal-backend
```

```bash
cd /home/ubuntu/sitecankartal/sitecankartal/Frontend
npm install && npm run build
sudo systemctl reload nginx
```

## Güvenlik

1. `.env` dosyasını Git'e commit etmeyin
2. `prod_SECRET_KEY` ve `prod_MYSQL_PASSWORD` güçlü olmalı
3. Gunicorn sadece `127.0.0.1` üzerinde dinlemeli (nginx reverse proxy)
4. SSL sertifikalarını düzenli kontrol edin: `sudo certbot renew --dry-run`
