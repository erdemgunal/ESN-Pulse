Mimari - ESN PULSE
Versiyon: 1.0.0 - 28.09.2025
Genel Bakış
ESN PULSE, etkinlik verilerini scrape eden, yerel PostgreSQL'de saklayan ve manuel CLI ile çalışan bir sistemdir. MVP, etkinlik isim/acıklamalarına odaklanır.
Mimari Bileşenler
1. Veri Kaynağı

data.json: Şube ID'leri (örn. esn-marmara).
activities.esn.org: Etkinlik listeleri (/organisation/<section_id>/activities).

2. Scraper Modülü

Dil: Python 3.12.
Kütüphaneler: aiohttp, BeautifulSoup4, Pydantic.
İşlev: Akıllı öncelik sistemi ile etkinlik listelerini scrape eder, Pydantic ile valide eder.
Öncelik Sistemi: En son scrape edilme zamanına göre şube öncelikleri belirlenir.
Metadata Tracking: Her şube için son scrape zamanı takip edilir.
Hata Yönetimi: HTTP hataları (failed_scrapes), veri hataları (validation_errors).

3. Veritabanı

PostgreSQL: Local, normalize şema (countries, sections, activities).
Bağlantı: asyncpg, connection pool.
Özellikler: FK'lar, index'ler, sonsuz saklama.

4. CLI

Komutlar: python run_scraper.py --section esn-marmara veya tüm şubeler.
Kütüphane: argparse.

5. Loglama

Dosya: logs/scrape.log.
Tablolar: failed_scrapes, validation_errors.

Veri Akışı

data.json → countries, sections tablolarına yüklenir.
Metadata Analizi → sections.last_scraped alanına göre öncelik sırası belirlenir.
Öncelikli Şubeler → Hiç scrape edilmemiş veya en eski scrape edilmiş şubeler önce işlenir.
sections.activities_platform_slug → etkinlik listeleri scrape edilir (pagination, 5'li chunk).
Veriler validate edilir, activities tablosuna kaydedilir.
sections.last_scraped → başarılı scrape sonrası güncellenir.
SQL sorguları ile etkinlikler listelenir.

Ölçeklenebilirlik

Asenkron HTTP (aiohttp) ile paralel scraping.
Akıllı öncelik sistemi ile verimli kaynak kullanımı.
5'li chunk'lar, 513 şube için optimize.
DB index'leri hızlı sorgulama için (last_scraped alanı dahil).

Dayanıklılık

HTTP retry: 3 kez, 0.5s delay.
Hata loglama: failed_scrapes, validation_errors.
