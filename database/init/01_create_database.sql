-- ESN PULSE Database Initialization Script
-- Bu script PostgreSQL container başlatıldığında otomatik çalışır

-- ESN PULSE database'ini oluştur (eğer yoksa)
SELECT 'CREATE DATABASE esn_pulse'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'esn_pulse')\gexec

-- ESN PULSE kullanıcısına gerekli izinleri ver
GRANT ALL PRIVILEGES ON DATABASE esn_pulse TO postgres;

-- Database'e bağlan
\c esn_pulse;

-- Extensions ekle
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- Core tabloları oluştur
\i /docker-entrypoint-initdb.d/schemas/01_core_tables.sql

-- İstatistik tablolarını oluştur
\i /docker-entrypoint-initdb.d/schemas/02_statistics_tables.sql

-- İzleme tablolarını oluştur
\i /docker-entrypoint-initdb.d/schemas/03_monitoring_tables.sql 