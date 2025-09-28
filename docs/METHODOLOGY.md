Yöntem - ESN PULSE
Versiyon: 1.0.0 - 28.09.2025
Genel Bakış
ESN PULSE, data.json'daki şube ID'lerini kullanarak etkinlik verilerini scrape eder, PostgreSQL'e kaydeder ve beyin fırtınası için sorgulanabilir hale getirir.
Adımlar
1. Veritabanı Hazırlığı

schema.sql ile countries, sections, activities, failed_scrapes, validation_errors tabloları oluşturulur.
data.json countries ve sections tablolarına yüklenir (load_data_json.py).

2. Etkinlik Scraping

Kaynak: https://activities.esn.org/organisation//activities.
Akıllı Öncelik Sistemi:
sections.last_scraped alanına göre şube öncelikleri belirlenir.
Hiç scrape edilmemiş şubeler (last_scraped = NULL) en yüksek öncelik.
En eski scrape edilmiş şubeler ikinci öncelik.
Süreç:
Öncelik sırasına göre sections.activities_platform_slug alınır.
İlk sayfada pagination kontrolü (<li class="pager__item--last">).
Sayfalar 5'li chunk'lara bölünür, aiohttp ile paralel scrape.
Veriler: title, description, city, country_code, participants, activity_type, start_date.
Pydantic ile validasyon, activities tablosuna UPSERT.
Başarılı scrape sonrası sections.last_scraped güncellenir.



3. Hata Yönetimi

HTTP hataları: 3 retry, failed_scrapes tablosuna log.
Veri hataları: validation_errors tablosuna log.

4. Sorgulama

SQL ile etkinlik listeleme (örn. SELECT title, description FROM activities WHERE city='Istanbul').

Çalıştırma

CLI: python run_scraper.py --section esn-marmara (belirli şube) veya --all (akıllı öncelik sistemi ile tüm şubeler).
Akıllı Mod: Program her çalıştırıldığında en az scrape edilmiş şubeleri otomatik olarak öncelik verir.
Loglar: logs/scrape.log.
