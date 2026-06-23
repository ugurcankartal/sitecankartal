# Frontend API Entegrasyonu

React frontend Django REST API'ye bağlandı.

## Yapılan Değişiklikler

### 1. API Servis Dosyası (`src/app/services/api.ts`)
- Tüm API endpoint'leri için TypeScript tipleri tanımlandı
- API çağrıları için fonksiyonlar oluşturuldu
- Base URL: `/api/v1` (production) veya Vite proxy ile dev

### 2. Icon Mapper (`src/app/utils/iconMapper.tsx`)
- String icon isimlerini Lucide React icon component'lerine çeviren utility
- Tüm icon mapping'ler merkezi bir yerde yönetiliyor

### 3. Component Güncellemeleri

#### Hero Section
- Profil bilgileri API'den çekiliyor
- Sosyal medya linkleri dinamik olarak gösteriliyor
- Loading state eklendi

#### About Section
- Timeline verileri API'den çekiliyor
- Skills verileri API'den çekiliyor
- Icon mapping ile dinamik icon gösterimi

#### Projects Section
- Tüm projeler API'den çekiliyor
- Proje detayları dinamik olarak gösteriliyor
- GitHub ve demo linkleri API'den geliyor

#### Blog Section
- Featured post ve normal posts API'den çekiliyor
- Tarih formatlaması eklendi
- Loading state eklendi

#### Contact Section
- İletişim formu API'ye bağlandı
- Form submit başarı/hata mesajları eklendi
- Profil bilgileri API'den çekiliyor
- Sosyal medya linkleri dinamik

## Kullanım

### Backend'i Başlatın
```bash
cd backend
python manage.py runserver 127.0.0.1:8000
```

> Eski Flask backend: `../backend-flask/` (legacy)

### Frontend'i Başlatın
```bash
cd Frontend
npm install  # veya pnpm install
npm run dev  # veya pnpm dev
```

### API Endpoint'leri

- `GET /api/profile` - Profil bilgileri
- `GET /api/timeline` - İş deneyimi timeline
- `GET /api/skills` - Yetenekler
- `GET /api/projects` - Projeler
- `GET /api/blog` - Blog yazıları
- `POST /api/contact` - İletişim formu gönderimi

## Notlar

- API base URL'i `src/app/services/api.ts` dosyasında tanımlı
- Production'da API URL'i environment variable olarak ayarlanmalı
- CORS ayarları backend'de yapılandırıldı (localhost:5173 ve localhost:3000)
