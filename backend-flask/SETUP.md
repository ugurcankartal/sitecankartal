# Kurulum Talimatları

## 1. Gereksinimler

- Python 3.8 veya üzeri
- MySQL Server (çalışır durumda)
- pip (Python paket yöneticisi)

## 2. Veritabanı Kurulumu

### MySQL'de veritabanını oluşturun:

```sql
CREATE DATABASE IF NOT EXISTS personal_portfolio CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

Veya `create_database.sql` dosyasını çalıştırabilirsiniz:

```bash
mysql -u root -p < create_database.sql
```

## 3. Python Bağımlılıklarını Yükleyin

```bash
cd backend
pip install -r requirements.txt
```

## 4. Veritabanını Başlatın

Örnek verilerle veritabanını doldurmak için:

```bash
python init_db.py
```

Bu script:
- Tüm tabloları oluşturur
- Örnek profil, projeler, blog yazıları, timeline ve skill verilerini ekler

## 5. Uygulamayı Başlatın

```bash
python app.py
```

veya

```bash
python run.py
```

API şu adreste çalışacak: `http://localhost:5000`

## 6. API'yi Test Edin

Tarayıcıda veya Postman ile test edebilirsiniz:

```bash
# Health check
curl http://localhost:5000/api/health

# Profil bilgilerini getir
curl http://localhost:5000/api/profile

# Projeleri getir
curl http://localhost:5000/api/projects

# Blog yazılarını getir
curl http://localhost:5000/api/blog
```

## Sorun Giderme

### MySQL bağlantı hatası
- MySQL servisinin çalıştığından emin olun
- `config.py` dosyasındaki veritabanı bilgilerini kontrol edin
- Kullanıcı adı ve şifrenin doğru olduğundan emin olun

### Port zaten kullanılıyor
- `app.py` dosyasındaki port numarasını değiştirin (varsayılan: 5000)
- Veya çalışan uygulamayı durdurun

### Modül bulunamadı hatası
- Tüm bağımlılıkların yüklendiğinden emin olun: `pip install -r requirements.txt`
- Virtual environment kullanıyorsanız aktif olduğundan emin olun
