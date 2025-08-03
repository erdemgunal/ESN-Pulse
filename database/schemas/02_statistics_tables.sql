-- ESN PULSE Statistics Tables Schema
-- Şube istatistiklerini saklayan tablolar

-- Section overall statistics - Genel şube istatistikleri
CREATE TABLE IF NOT EXISTS section_overall_statistics (
    id SERIAL PRIMARY KEY,
    section_id INTEGER REFERENCES sections(id) ON DELETE CASCADE,
    
    -- Activity counts by type
    physical_activities INTEGER DEFAULT 0,
    online_activities INTEGER DEFAULT 0,
    
    -- Participant counts by type
    total_local_students INTEGER DEFAULT 0,
    total_international_students INTEGER DEFAULT 0,
    total_coordinators INTEGER DEFAULT 0,
    
    scraped_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(section_id)
);

-- Section cause statistics - Nedenlere göre istatistikler
CREATE TABLE IF NOT EXISTS section_cause_statistics (
    id SERIAL PRIMARY KEY,
    section_id INTEGER REFERENCES sections(id) ON DELETE CASCADE,
    cause_name VARCHAR(100) NOT NULL,
    
    total_count INTEGER DEFAULT 0,
    physical_count INTEGER DEFAULT 0,
    online_count INTEGER DEFAULT 0,
    
    scraped_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(section_id, cause_name)
);

-- Section type statistics - Türlere göre istatistikler
CREATE TABLE IF NOT EXISTS section_type_statistics (
    id SERIAL PRIMARY KEY,
    section_id INTEGER REFERENCES sections(id) ON DELETE CASCADE,
    activity_type VARCHAR(100) NOT NULL,
    
    physical_count INTEGER DEFAULT 0,
    online_count INTEGER DEFAULT 0,
    
    scraped_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(section_id, activity_type)
);

-- Section participant statistics - Katılımcı türlerine göre istatistikler
CREATE TABLE IF NOT EXISTS section_participant_statistics (
    id SERIAL PRIMARY KEY,
    section_id INTEGER REFERENCES sections(id) ON DELETE CASCADE,
    participant_type VARCHAR(100) NOT NULL,
    
    physical_count INTEGER DEFAULT 0,
    online_count INTEGER DEFAULT 0,
    
    scraped_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(section_id, participant_type)
);

-- Statistics performance indexes
CREATE INDEX IF NOT EXISTS idx_section_overall_stats_section_id ON section_overall_statistics(section_id);
CREATE INDEX IF NOT EXISTS idx_section_cause_stats_section_id ON section_cause_statistics(section_id);
CREATE INDEX IF NOT EXISTS idx_section_type_stats_section_id ON section_type_statistics(section_id);
CREATE INDEX IF NOT EXISTS idx_section_participant_stats_section_id ON section_participant_statistics(section_id);

-- Composite indexes for queries
CREATE INDEX IF NOT EXISTS idx_section_cause_stats_lookup ON section_cause_statistics(section_id, cause_name);
CREATE INDEX IF NOT EXISTS idx_section_type_stats_lookup ON section_type_statistics(section_id, activity_type);
CREATE INDEX IF NOT EXISTS idx_section_participant_stats_lookup ON section_participant_statistics(section_id, participant_type); 