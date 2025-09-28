Veri Seti Özellikleri - ESN PULSE
Versiyon: 1.0.0 - 28.09.2025
Genel Bakış
ESN PULSE, data.json ve activities.esn.org'dan etkinlik verilerini toplar ve PostgreSQL'de normalize bir şemada saklar. Veri seti, etkinlik isim/acıklamalarını beyin fırtınası için sağlar.
Tablolar
1. countries

Amaç: data.json'dan ülke verileri.
Alanlar:
country_code: VARCHAR(10), PK, örn. "TR".
name: VARCHAR(100), örn. "Türkiye".
url: VARCHAR(255), örn. "/country/tr".


Kaynak: data.json.countries[].

2. sections

Amaç: Şube bilgileri ve scraping metadata'sı.
Alanlar:
id: SERIAL, PK.
activities_platform_slug: VARCHAR(255), UNIQUE, örn. "esn-marmara".
name: VARCHAR(255), örn. "ESN Marmara".
city: VARCHAR(100), örn. "Istanbul".
country_code: VARCHAR(10), FK → countries.
last_scraped: TIMESTAMP, son başarılı scrape zamanı (NULL = hiç scrape edilmemiş).
scrape_count: INTEGER DEFAULT 0, toplam başarılı scrape sayısı.
last_attempt: TIMESTAMP, son scrape deneme zamanı (başarılı/başarısız).
status: VARCHAR(20) DEFAULT 'pending', scraping durumu ('pending', 'in_progress', 'completed', 'failed').


Kaynak: data.json.countries[].branches[] + scraping metadata.

3. activities

Amaç: Etkinlik verileri.
Alanlar:
id: SERIAL, PK.
event_slug: VARCHAR(255), UNIQUE, örn. "boat-party-20885".
title: VARCHAR(255), örn. "Boat Party".
description: TEXT, etkinlik açıklaması.
city: VARCHAR(100), örn. "Istanbul".
country_code: VARCHAR(10), FK → countries.
participants: INTEGER, CHECK (>=0).
activity_type: VARCHAR(100), örn. "Game or Social Activity".
start_date: DATE, örn. "2023-11-08".
is_future_event: BOOLEAN, gelecek/geçmiş.
section_id: INTEGER, FK → sections.
is_valid: BOOLEAN, veri doğruluğu.


Kaynak: activities.esn.org/organisation//activities.

4. failed_scrapes

Amaç: HTTP hataları.
Alanlar:
id: SERIAL, PK.
scraper_module: VARCHAR(50), örn. "activities".
url: VARCHAR(255).
http_status_code: INTEGER.
error_message: TEXT.
retry_count: INTEGER.
created_at: TIMESTAMP.



5. validation_errors

Amaç: Veri validasyon hataları.
Alanlar:
id: SERIAL, PK.
scraper_module: VARCHAR(50).
error_type: VARCHAR(100).
error_data: TEXT.
created_at: TIMESTAMP.



Veri Formatları

Tarihler: ISO (YYYY-MM-DD).
Katılımcılar: Negatif olmayan tamsayı.
Zorunlu Alanlar: event_slug, title, section_id.
Opsiyonel: description, city, participants, activity_type, start_date.

Validasyon

Pydantic ile: Boş title yok, negatif participants yok.
Hatalar validation_errors tablosuna loglanır.

Saklama

Veriler silinmez, sonsuz saklama.
Index'ler: section_id, city, is_valid, last_scraped (sections tablosu için).
Öncelik Sorguları: last_scraped ASC NULLS FIRST ile hiç scrape edilmemiş şubeler önce gelir.
