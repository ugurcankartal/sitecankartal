# Admin Panel Kullanım Kılavuzu

## Giriş

Admin paneline `http://localhost:5000/admin` adresinden erişebilirsiniz.

## İlk Kurulum

1. Veritabanını başlatın:
   ```bash
   python init_db.py
   ```

2. Varsayılan kullanıcı bilgileri:
   - **Kullanıcı Adı:** `admin`
   - **Şifre:** `admin123`
   
   ⚠️ **ÖNEMLİ:** İlk girişten sonra mutlaka şifrenizi değiştirin!

## Özellikler

### 1. Genel Bakış
- Toplam proje sayısı
- Toplam blog yazısı sayısı
- Toplam mesaj sayısı

### 2. Profil Yönetimi
- Kişisel bilgileri güncelleme (Ad Soyad, E-posta, Telefon, Konum, Biyografi)
- Şifre değiştirme

### 3. Projeler
- Tüm projeleri görüntüleme
- Proje düzenleme (yakında)

### 4. Blog
- Tüm blog yazılarını görüntüleme
- Blog yazısı düzenleme (yakında)

### 5. Mesajlar
- İletişim formundan gelen tüm mesajları görüntüleme
- Mesaj detaylarını inceleme

## API Endpoint'leri

### Authentication
- `POST /api/auth/login` - Giriş yap
- `POST /api/auth/logout` - Çıkış yap
- `GET /api/auth/check` - Oturum kontrolü

### Admin
- `GET /api/admin/user` - Kullanıcı bilgilerini getir
- `PUT /api/admin/user` - Kullanıcı bilgilerini güncelle
- `PUT /api/admin/user/password` - Şifre değiştir

## Güvenlik Notları

1. **User Tablosu:** Sistemde sadece 1 kullanıcı olabilir (database constraint ile korunmuştur)
2. **Session Yönetimi:** Flask-Session kullanılarak oturum yönetimi yapılmaktadır
3. **Şifre Hashleme:** Werkzeug'un güvenli şifre hashleme fonksiyonu kullanılmaktadır
4. **CORS:** Admin paneli backend ile aynı origin'de çalıştığı için CORS sorunu yoktur

## Sorun Giderme

### Giriş yapamıyorum
- Kullanıcı adı ve şifrenin doğru olduğundan emin olun
- Veritabanının başlatıldığından emin olun (`python init_db.py`)
- Backend'in çalıştığından emin olun

### Session kayboluyor
- Tarayıcı çerezlerinin etkin olduğundan emin olun
- `SESSION_TYPE` ayarının `config.py`'de doğru olduğundan emin olun
