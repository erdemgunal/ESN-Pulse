-- ESN PULSE Monitoring and Error Tracking Tables
-- İzleme ve hata takibi için tablolar

-- Scraper status - Scraper çalışma durumu
CREATE TABLE IF NOT EXISTS scraper_status (
    id SERIAL PRIMARY KEY,
    scraper_module VARCHAR(50) NOT NULL,
    status VARCHAR(20) NOT NULL,
    started_at TIMESTAMP NOT NULL DEFAULT NOW(),
    completed_at TIMESTAMP,
    sections_processed INTEGER DEFAULT 0,
    sections_failed INTEGER DEFAULT 0,
    error_message TEXT,
    metadata JSONB
);

-- Validation errors - Veri doğrulama hataları
CREATE TABLE IF NOT EXISTS validation_errors (
    id SERIAL PRIMARY KEY,
    section_id INTEGER REFERENCES sections(id),
    activity_event_slug VARCHAR(255),
    field_name VARCHAR(100),
    error_message TEXT NOT NULL,
    raw_data JSONB,
    scraper_module VARCHAR(50),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Failed scrapes - Başarısız HTTP istekleri
CREATE TABLE IF NOT EXISTS failed_scrapes (
    id SERIAL PRIMARY KEY,
    url VARCHAR(500) NOT NULL,
    section_id INTEGER REFERENCES sections(id),
    scraper_module VARCHAR(50),
    http_status_code INTEGER,
    error_message TEXT,
    retry_count INTEGER DEFAULT 0,
    last_attempt TIMESTAMP DEFAULT NOW(),
    will_retry BOOLEAN DEFAULT TRUE
);

-- Monitoring indexes
CREATE INDEX IF NOT EXISTS idx_scraper_status_module ON scraper_status(scraper_module);
CREATE INDEX IF NOT EXISTS idx_scraper_status_started ON scraper_status(started_at DESC);
CREATE INDEX IF NOT EXISTS idx_validation_errors_created ON validation_errors(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_failed_scrapes_retry ON failed_scrapes(will_retry) WHERE will_retry = TRUE;
CREATE INDEX IF NOT EXISTS idx_failed_scrapes_module ON failed_scrapes(scraper_module); 