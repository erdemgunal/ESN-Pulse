# ESN PULSE - ESN Network Data Scraper & Analytics Platform

**Version:** 1.0.0  
**Status:** Development  

ESN PULSE, 46 ülke ve 517 ESN şubesinin verilerini otomatik olarak toplayan, işleyen ve analiz için hazır hale getiren kapsamlı bir veri scraping ve analitik platformudur.

## 🎯 Temel Özellikler

- **Otomatik Veri Toplama**: `accounts.esn.org` ve `activities.esn.org` platformlarından düzenli veri çekme
- **Asenkron İşleme**: Yüksek performanslı paralel veri işleme
- **Güvenilir Mimari**: Hata yönetimi ve kurtarma mekanizmaları
- **BI Entegrasyonu**: Power BI, Tableau gibi araçlarla uyumlu veri yapısı
- **Ölçeklenebilir Tasarım**: 517 şubeden gelen veri yoğunluğunu kaldırabilen mimari

## 🏗️ Sistem Mimarisi

```
┌─────────────────────────────────────────────────────┐
│                ESN PULSE ARCHITECTURE               │
├─────────────────────────────────────────────────────┤
│                                                     │
│  ┌─────────────┐    ┌─────────────┐    ┌──────────┐ │
│  │   DATA      │    │  SCRAPING   │    │   DATA   │ │
│  │  SOURCES    │───▶│   ENGINE    │───▶│ STORAGE  │ │
│  │             │    │             │    │          │ │
│  │ accounts.   │    │ AccountsSc- │    │ PostgreS │ │
│  │ esn.org     │    │ raper       │    │ QL       │ │
│  │             │    │             │    │          │ │
│  │ activities. │    │ Activities- │    │ Redis    │ │
│  │ esn.org     │    │ Scraper     │    │ (Queue)  │ │
│  └─────────────┘    └─────────────┘    └──────────┘ │
│                                                     │
└─────────────────────────────────────────────────────┘
```

## 🚀 Hızlı Başlangıç

### Gereksinimler

- Python 3.11+
- Docker & Docker Compose
- PostgreSQL 15+
- Redis 7+

### Kurulum

1. **Projeyi klonlayın:**
```bash
git clone https://github.com/erdemgunal/esn_pulse.git
cd esn_pulse
```

2. **Environment dosyasını oluşturun:**
```bash
cp .env.example .env
# .env dosyasını düzenleyin
```

3. **Docker ile başlatın:**
```bash
docker-compose up -d
```

4. **Veritabanı migration'larını çalıştırın:**
```bash
docker-compose exec app python -m alembic upgrade head
```

### Manuel Kurulum

1. **Virtual environment oluşturun:**
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate  # Windows
```

2. **Bağımlılıkları yükleyin:**
```bash
pip install -r requirements.txt
```

3. **Veritabanını başlatın:**
```bash
# PostgreSQL ve Redis'in çalıştığından emin olun
createdb esn_pulse
alembic upgrade head
```

## 📋 Kullanım

### CLI Komutları

```bash
# Tüm scraper'ları çalıştır
python -m src.cli.main --module all

# Sadece countries ve sections bilgilerini çek
python -m src.cli.main --module accounts

# Sadece activities ve statistics bilgilerini çek  
python -m src.cli.main --module activities

# Belirli bir şube için activities çek
python -m src.cli.main --module activities --section esn-metu

# Sağlık kontrolü
python -m src.cli.main --health-check
```

### Celery Görevleri

```bash
# Worker başlat
celery -A src.tasks.celery_app worker --loglevel=info

# Beat scheduler başlat (otomatik görevler için)
celery -A src.tasks.celery_app beat --loglevel=info

# Flower monitoring başlat
celery -A src.tasks.celery_app flower
```

## 📊 Veri Modeli

### Core Tablolar

- **`countries`**: 46 ESN ülkesi
- **`sections`**: 517 ESN şubesi
- **`activities`**: Şube etkinlikleri
- **`section_*_statistics`**: Şube istatistikleri

### İlişki Tabloları

- **`activity_section_organisers`**: Etkinlik-Şube ilişkisi
- **`activity_to_cause`**: Etkinlik-Neden ilişkisi
- **`activity_to_sdg`**: Etkinlik-SDG ilişkisi
- **`activity_to_objective`**: Etkinlik-Hedef ilişkisi

## 🔧 Konfigürasyon

### Environment Variables

```env
# Database
DATABASE_URL=postgresql://user:pass@localhost:5432/esn_pulse

# Scraping Settings
SCRAPING_DELAY=0.5          # İstekler arası gecikme (saniye)
MAX_RETRIES=3               # Maksimum yeniden deneme
REQUEST_TIMEOUT=30          # İstek timeout (saniye)

# Performance
PAGINATION_CHUNK_SIZE=5     # Paralel sayfa işleme boyutu
BULK_INSERT_BATCH_SIZE=100  # Toplu insert boyutu
```

### Scraper Ayarları

- **Rate Limiting**: 0.5 saniye gecikme (1 istek/saniye)
- **User-Agent Rotation**: Bot detection'ı önlemek için
- **Retry Logic**: Üstel geri çekilme ile 3 yeniden deneme
- **Error Handling**: Kapsamlı hata yönetimi ve logging

## 📈 Performans ve Ölçeklenebilirlik

### Hedef Performans

- **Full scrape süresi**: < 2 saat (517 şube)
- **HTTP başarı oranı**: > 95%
- **Veri validation başarısı**: > 98%
- **Veritabanı sorgu süresi**: < 100ms (95th percentile)

### Ölçeklenebilirlik Özellikleri

- **Asenkron İşleme**: `asyncio` ve `aiohttp` ile yüksek eşzamanlılık
- **Connection Pooling**: PostgreSQL bağlantı havuzu
- **Horizontal Scaling**: Celery worker'ları farklı makinelerde
- **Caching Strategy**: Redis ile önbellekleme

## 🧪 Test

```bash
# Tüm testleri çalıştır
pytest

# Coverage ile
pytest --cov=src --cov-report=html

# Belirli bir modülü test et
pytest tests/unit/test_scrapers.py

# Integration testleri
pytest tests/integration/
```

## 📝 Logging ve Monitoring

### Log Seviyeleri

- **DEBUG**: Detaylı debugging bilgileri
- **INFO**: Genel işlem bilgileri
- **WARNING**: Uyarı mesajları
- **ERROR**: Hata mesajları
- **CRITICAL**: Kritik sistem hataları

### Monitoring Tablolar

- **`scraper_status`**: Scraper çalışma geçmişi
- **`validation_errors`**: Veri doğrulama hataları  
- **`failed_scrapes`**: Başarısız HTTP istekleri

## 🔐 Güvenlik

- **Rate Limiting**: Platformlara yük bindirmemek için
- **User-Agent Rotation**: Bot detection önleme
- **Input Validation**: SQL injection koruması
- **HTTPS Zorunlu**: Tüm external requests için
- **Environment Variables**: Hassas bilgiler için

## 🤝 Katkıda Bulunma

1. Fork yapın
2. Feature branch oluşturun (`git checkout -b feature/amazing-feature`)
3. Değişikliklerinizi commit edin (`git commit -m 'Add amazing feature'`)
4. Branch'inizi push edin (`git push origin feature/amazing-feature`)
5. Pull Request oluşturun

## 📄 Lisans

Bu proje [MIT License](LICENSE) altında lisanslanmıştır.

## 📞 Destek

- **Email**: esnpulse@example.com
- **Documentation**: [docs/](docs/)
- **Issues**: [GitHub Issues](https://github.com/erdemgunal/esn_pulse/issues)

## 🚧 Geliştirme Roadmap

### Faz 1 (Mevcut)
- ✅ Core scraping engine
- ✅ Database schema
- ✅ CLI interface
- ✅ Docker containerization

### Faz 2 (Planlanan)
- 🔄 Web dashboard (FastAPI)
- 🔄 Real-time monitoring
- 🔄 Advanced analytics
- 🔄 Multi-tenant support

### Faz 3 (Gelecek)
- 📅 Machine learning integration
- 📅 Predictive analytics
- 📅 Mobile API
- 📅 Social media integration

---

**ESN PULSE** - Empowering ESN network with data-driven insights 🚀 