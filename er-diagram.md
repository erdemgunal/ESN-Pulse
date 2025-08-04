```erDiagram
    countries {
        VARCHAR country_code PK "Ülke Kodu (örn. TR)"
        VARCHAR name "Ülke Adı"
        VARCHAR slug "Slug"
        VARCHAR url "URL"
        INTEGER section_count "Şube Sayısı"
    }

    sections {
        SERIAL id PK "Şube ID"
        VARCHAR accounts_platform_slug "accounts.esn.org slug"
        VARCHAR activities_platform_slug "activities.esn.org slug"
        VARCHAR name "Şube Adı"
        VARCHAR accounts_url "Accounts Platform URL"
        VARCHAR activities_url "Activities Platform URL"
        VARCHAR logo_url "Logo URL"
        VARCHAR city "Şehir"
        VARCHAR address "Adres"
        VARCHAR email "E-posta"
        JSONB social_media "Sosyal Medya Linkleri"
        DECIMAL latitude "Enlem"
        DECIMAL longitude "Boylam"
        VARCHAR website "Web Sitesi"
        VARCHAR university_name "Üniversite Adı"
        VARCHAR country_code FK "Ülke Kodu"
        BOOLEAN can_scrape_activities "Activities çekilebilir mi"
        TIMESTAMP last_validated_activities_slug "Son Slug Doğrulama"
        TIMESTAMP last_scraped "Son Scrape Zamanı"
    }

    activities {
        SERIAL id PK "Etkinlik ID"
        VARCHAR event_slug "Etkinlik Slug"
        VARCHAR title "Başlık"
        VARCHAR url "URL"
        TEXT description "Açıklama"
        DATE start_date "Başlangıç Tarihi"
        DATE end_date "Bitiş Tarihi"
        VARCHAR city "Şehir"
        VARCHAR country_code "Ülke Kodu"
        INTEGER participants "Katılımcı Sayısı"
        VARCHAR activity_type "Etkinlik Türü"
        BOOLEAN is_future_event "Gelecek Etkinlik mi"
        BOOLEAN is_valid "Geçerli mi"
    }

    activity_causes {
        SERIAL id PK "Neden ID"
        VARCHAR name "Neden Adı"
    }
    
    sdgs {
        SERIAL id PK "SDG ID"
        VARCHAR name "SDG Adı"
    }

    objectives {
        SERIAL id PK "Hedef ID"
        VARCHAR name "Hedef Adı"
    }

    activity_section_organisers {
        INTEGER activity_id FK "Etkinlik ID"
        INTEGER section_id FK "Şube ID"
    }

    activity_to_cause {
        INTEGER activity_id FK "Etkinlik ID"
        INTEGER cause_id FK "Neden ID"
    }

    activity_to_sdg {
        INTEGER activity_id FK "Etkinlik ID"
        INTEGER sdg_id FK "SDG ID"
    }

    activity_to_objective {
        INTEGER activity_id FK "Etkinlik ID"
        INTEGER objective_id FK "Hedef ID"
    }

    scraper_status {
        SERIAL id PK "Durum ID"
        VARCHAR scraper_module "Scraper Modülü"
        TIMESTAMP last_run "Son Çalışma Zamanı"
        VARCHAR status "Durum (Başarılı/Başarısız)"
        TEXT error_message "Hata Mesajı"
    }

    validation_errors {
        SERIAL id PK "Hata ID"
        VARCHAR scraper_module "Hata Oluşan Modül"
        VARCHAR error_type "Hata Türü"
        TEXT error_data "Hatalı Veri (JSON)"
        TIMESTAMP created_at "Oluşturma Zamanı"
    }
    
    failed_scrapes {
        SERIAL id PK "Hata ID"
        VARCHAR scraper_module "Hata Oluşan Modül"
        VARCHAR url "Hatalı URL"
        INTEGER http_status_code "HTTP Durum Kodu"
        TEXT error_message "Hata Mesajı"
        INTEGER retry_count "Yeniden Deneme Sayısı"
        TIMESTAMP created_at "Oluşturma Zamanı"
    }

    section_overall_statistics {
        SERIAL id PK
        INTEGER section_id FK "Şube ID"
        INTEGER physical_activities
        INTEGER online_activities
        INTEGER total_local_students "Toplam Yerel Öğrenci"
        INTEGER total_international_students "Toplam Uluslararası Öğrenci"
        INTEGER total_coordinators "Toplam Koordinatör"
    }
    
    section_cause_statistics {
        SERIAL id PK
        INTEGER section_id FK "Şube ID"
        VARCHAR cause_name
        INTEGER physical_activities
        INTEGER online_activities
    }
    
    section_type_statistics {
        SERIAL id PK
        INTEGER section_id FK "Şube ID"
        VARCHAR type_name
        INTEGER physical_activities
        INTEGER online_activities
    }
    
    section_participant_statistics {
        SERIAL id PK
        INTEGER section_id FK "Şube ID"
        VARCHAR participant_type
        INTEGER physical_activities
        INTEGER online_activities
    }
    
    countries ||--o{ sections : "is located in"
    sections ||--o{ section_overall_statistics : "has"
    sections ||--o{ section_cause_statistics : "has"
    sections ||--o{ section_type_statistics : "has"
    sections ||--o{ section_participant_statistics : "has"
    
    activities }|--|{ activity_section_organisers : "organised by"
    activities }|--|{ activity_to_cause : "has"
    activities }|--|{ activity_to_sdg : "has"
    activities }|--|{ activity_to_objective : "has"

    sections }|--|{ activity_section_organisers : "organises"
    activity_causes }|--|{ activity_to_cause : "has"
    sdgs }|--|{ activity_to_sdg : "has"
    objectives }|--|{ activity_to_objective : "has"```
