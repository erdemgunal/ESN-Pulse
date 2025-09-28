Ürün Gereksinim Dokümanı (PRD) - ESN PULSE
Versiyon: 1.0.4 - 28.09.2025
1. Giriş
ESN PULSE, ESN (Erasmus Student Network) şubelerinin etkinlik verilerini scrape ederek ESN Marmara için yenilikçi etkinlik fikirleri üretmek amacıyla geliştirilen bir veri toplama aracıdır. Proje, data.json dosyasındaki 513 şube ID'sini kullanarak activities.esn.org/organisation/<id>/activities adreslerinden etkinlik verilerini çeker, PostgreSQL veritabanına kaydeder ve beyin fırtınası için sorgulanabilir hale getirir. MVP, manuel CLI ile çalışır ve etkinlik isimleri/acıklamalarına odaklanır.
Stakeholder Bağlamı: ESN Marmara gönüllüleri için yerel makinede çalışacak bir araç. Gelecekte AI entegrasyonu (Faz 3) ile etkinlik önerileri üretilecek.
2. Amaç ve Hedefler
2.1. Temel Amaç
ESN şubelerinin etkinlik verilerini (başlık, açıklama, şehir, vb.) toplayarak ESN Marmara için etkinlik önerileri üretmek için veri tabanı oluşturmak.
2.2. Hedefler

Veri Toplama: data.json'daki şube ID'lerini kullanarak activities.esn.org'dan etkinlik verilerini scrape etmek.
Veri Depolama: Etkinlikleri normalize bir PostgreSQL DB'de saklamak.
Manuel Çalıştırma: CLI ile tetikleme (örn. python run_scraper.py --section esn-marmara).
Hata Yönetimi: HTTP ve veri hatalarını loglama (failed_scrapes, validation_errors).
Sorgulama: SQL ile etkinlik listesi çıkarma (örn. İstanbul etkinlikleri).
Ölçeklenebilirlik: 513 şube ve tahmini 10k+ etkinlik için performans.

2.3. Uyumluluk ve Etik

Sadece halka açık HTML verileri scrape edilecek (authentication yok).
GDPR: Kişisel veri toplanmayacak.
ESN International ile scraping izni için iletişim kurulacak.

3. Kapsam
3.1. Veri Kaynakları

data.json: 45 ülke, 513 şube (ID'ler, şehir, ülke kodu).
activities.esn.org: Etkinlik listesi (/organisation//activities, pagination ile).

3.2. Çekilecek Veri Kategorileri

Ülkeler (countries): country_code, name, url (data.json'dan).
Şubeler (sections): activities_platform_slug, name, city, country_code (data.json'dan).
Etkinlikler (activities): event_slug, title, description, city, country_code, participants, activity_type, start_date, is_future_event, section_id.

3.3. Kapsam Dışı

SDG, causes, objectives verileri.
İstatistik verileri (/statistics).
Otomatik scheduling, AI entegrasyonu (Faz 3), web arayüzü.
Veri silme (sonsuz saklama).

3.4. Veri Tazeliği

Manuel tetikleme, kullanıcı istediğinde çalışır.

4. Teknik Mimari
4.1. Genel Bakış
Python tabanlı scraper, local Postgres DB, asenkron HTTP istekleri. Docker Compose ile konteynerleştirme.
4.2. Bileşenler

Scraper: Python, aiohttp, BeautifulSoup4, Pydantic.
DB: Local PostgreSQL, asyncpg.
CLI: argparse ile manuel tetikleme.
Hata Logları: failed_scrapes, validation_errors tabloları.

5. Veri Akışı

data.json'dan ülkeler ve şubeler DB'ye yüklenir.
Şube ID'leriyle etkinlik listeleri scrape edilir (5'li chunk'larla paralel).
Veriler Pydantic ile valide edilir, DB'ye kaydedilir.
SQL sorguları ile etkinlikler listelenir.

6. Ölçeklenebilirlik ve Hata Yönetimi

Paralel Scraping: 5'li sayfa chunk'ları ile asenkron istekler.
Hata Yönetimi: HTTP hataları için 3 retry, loglama.
Yedekleme: Manuel pg_dump.

7. Gelecek Geliştirmeler

Faz 2: Basit CLI sorgu araçları.
Faz 3: AI (Gemini/RAG) ile etkinlik önerileri.

8. Dokümantasyon

TECHNICAL_STACK.md, ARCHITECTURE.md, DATASET_SPECIFICATIONS.md, METHODOLOGY.md.
README.md (sonraki adım).