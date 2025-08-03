-- ESN PULSE Core Tables Schema
-- ER diagram'a göre ana tabloları oluşturur

-- Countries table - 46 ESN ülkesi
CREATE TABLE IF NOT EXISTS countries (
    country_code VARCHAR(10) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    slug VARCHAR(100) NOT NULL UNIQUE,
    url VARCHAR(255) NOT NULL,
    section_count INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Sections table - 517 ESN şubesi  
CREATE TABLE IF NOT EXISTS sections (
    id SERIAL PRIMARY KEY,
    country_code VARCHAR(10) REFERENCES countries(country_code) ON UPDATE CASCADE ON DELETE SET NULL,
    
    -- Platform slugs
    accounts_platform_slug VARCHAR(255) UNIQUE NOT NULL,
    activities_platform_slug VARCHAR(255),
    
    -- Basic info
    name VARCHAR(255) NOT NULL,
    accounts_url VARCHAR(255),
    activities_url VARCHAR(255),
    logo_url VARCHAR(255),
    
    -- Location info
    city VARCHAR(100),
    address TEXT,
    latitude DECIMAL(9,6),
    longitude DECIMAL(9,6),
    
    -- Contact info
    email VARCHAR(255),
    website VARCHAR(255),
    social_media JSONB,
    university_name VARCHAR(255),
    
    -- Scraping control
    can_scrape_activities BOOLEAN DEFAULT NULL,
    last_validated_activities_slug TIMESTAMP,
    last_scraped TIMESTAMP,
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Activity lookup tables
CREATE TABLE IF NOT EXISTS activity_causes (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS sdgs (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS objectives (
    id SERIAL PRIMARY KEY,
    name VARCHAR(200) UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Activities table - Ana etkinlik verisi
CREATE TABLE IF NOT EXISTS activities (
    id SERIAL PRIMARY KEY,
    event_slug VARCHAR(255) UNIQUE NOT NULL,
    url VARCHAR(255) NOT NULL,
    title VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
    
    -- Temporal data
    start_date DATE NOT NULL,
    end_date DATE,
    is_future_event BOOLEAN NOT NULL,
    
    -- Location
    city VARCHAR(100),
    country_code VARCHAR(10),
    
    -- Participation
    participants INTEGER CHECK (participants >= 0),
    activity_type VARCHAR(100),
    
    -- Data quality
    is_valid BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    
    -- Foreign key
    CONSTRAINT fk_activities_country 
        FOREIGN KEY (country_code) REFERENCES countries(country_code)
        ON UPDATE CASCADE ON DELETE SET NULL
);

-- Junction tables for Many-to-Many relationships
CREATE TABLE IF NOT EXISTS activity_section_organisers (
    activity_id INTEGER REFERENCES activities(id) ON DELETE CASCADE,
    section_id INTEGER REFERENCES sections(id) ON DELETE CASCADE,
    PRIMARY KEY (activity_id, section_id)
);

CREATE TABLE IF NOT EXISTS activity_to_cause (
    activity_id INTEGER REFERENCES activities(id) ON DELETE CASCADE,
    cause_id INTEGER REFERENCES activity_causes(id) ON DELETE CASCADE,
    PRIMARY KEY (activity_id, cause_id)
);

CREATE TABLE IF NOT EXISTS activity_to_sdg (
    activity_id INTEGER REFERENCES activities(id) ON DELETE CASCADE,
    sdg_id INTEGER REFERENCES sdgs(id) ON DELETE CASCADE,
    PRIMARY KEY (activity_id, sdg_id)
);

CREATE TABLE IF NOT EXISTS activity_to_objective (
    activity_id INTEGER REFERENCES activities(id) ON DELETE CASCADE,
    objective_id INTEGER REFERENCES objectives(id) ON DELETE CASCADE,
    PRIMARY KEY (activity_id, objective_id)
);

-- Performance indexes
CREATE INDEX IF NOT EXISTS idx_sections_can_scrape ON sections(can_scrape_activities) WHERE can_scrape_activities = TRUE;
CREATE INDEX IF NOT EXISTS idx_sections_last_scraped ON sections(last_scraped ASC NULLS FIRST);
CREATE INDEX IF NOT EXISTS idx_activities_start_date ON activities(start_date);
CREATE INDEX IF NOT EXISTS idx_activities_country ON activities(country_code);
CREATE INDEX IF NOT EXISTS idx_activities_valid ON activities(is_valid) WHERE is_valid = TRUE; 