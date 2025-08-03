"""
ESN PULSE Database Operations

Bu modül, veritabanı işlemlerini yönetir.
"""

import logging
from typing import Any, Dict, List, Optional, Tuple, Union

from asyncpg import Connection, Record

from .connection import get_database_connection

logger = logging.getLogger(__name__)

class DatabaseOperations:
    """Veritabanı işlemlerini yöneten sınıf."""
    
    def __init__(self):
        """DatabaseOperations sınıfını başlatır."""
        self.conn: Optional[Connection] = None
        self.db = None
    
    async def __aenter__(self):
        """Async context manager entry."""
        async with get_database_connection() as db:
            self.db = db
            self.conn = await db.pool.acquire()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self.conn:
            await self.db.pool.release(self.conn)
            self.conn = None
    
    async def insert_country(self, country_data: Dict[str, Any]) -> Record:
        """Ülke verisi ekler veya günceller.
        
        Args:
            country_data: Ülke verisi
        
        Returns:
            Eklenen/güncellenen ülke kaydı
        """
        query = """
            INSERT INTO countries (country_code, name, slug, url, section_count)
            VALUES ($1, $2, $3, $4, $5)
            ON CONFLICT (country_code) DO UPDATE
            SET name = EXCLUDED.name,
                slug = EXCLUDED.slug,
                url = EXCLUDED.url,
                section_count = EXCLUDED.section_count,
                updated_at = NOW()
            RETURNING *
        """
        return await self.conn.fetchrow(
            query,
            country_data['country_code'],
            country_data['name'],
            country_data['slug'],
            country_data['url'],
            country_data['section_count']
        )
    
    async def insert_section(self, section_data: Dict[str, Any]) -> Record:
        """Şube verisi ekler veya günceller.
        
        Args:
            section_data: Şube verisi
        
        Returns:
            Eklenen/güncellenen şube kaydı
        """
        query = """
            INSERT INTO sections (
                country_code, accounts_platform_slug, activities_platform_slug,
                name, accounts_url, activities_url, logo_url,
                city, address, latitude, longitude,
                email, website, social_media, university_name,
                can_scrape_activities, last_validated_activities_slug
            )
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, $16, $17)
            ON CONFLICT (accounts_platform_slug) DO UPDATE
            SET country_code = EXCLUDED.country_code,
                activities_platform_slug = EXCLUDED.activities_platform_slug,
                name = EXCLUDED.name,
                accounts_url = EXCLUDED.accounts_url,
                activities_url = EXCLUDED.activities_url,
                logo_url = EXCLUDED.logo_url,
                city = EXCLUDED.city,
                address = EXCLUDED.address,
                latitude = EXCLUDED.latitude,
                longitude = EXCLUDED.longitude,
                email = EXCLUDED.email,
                website = EXCLUDED.website,
                social_media = EXCLUDED.social_media,
                university_name = EXCLUDED.university_name,
                can_scrape_activities = EXCLUDED.can_scrape_activities,
                last_validated_activities_slug = EXCLUDED.last_validated_activities_slug,
                updated_at = NOW()
            RETURNING *
        """
        return await self.conn.fetchrow(
            query,
            section_data['country_code'],
            section_data['accounts_platform_slug'],
            section_data['activities_platform_slug'],
            section_data['name'],
            section_data['accounts_url'],
            section_data['activities_url'],
            section_data['logo_url'],
            section_data['city'],
            section_data['address'],
            section_data['latitude'],
            section_data['longitude'],
            section_data['email'],
            section_data['website'],
            section_data['social_media'],
            section_data['university_name'],
            section_data['can_scrape_activities'],
            section_data['last_validated_activities_slug']
        )
    
    async def insert_activity(self, activity_data: Dict[str, Any]) -> Record:
        """Etkinlik verisi ekler veya günceller.
        
        Args:
            activity_data: Etkinlik verisi
        
        Returns:
            Eklenen/güncellenen etkinlik kaydı
        """
        query = """
            INSERT INTO activities (
                event_slug, url, title, description,
                start_date, end_date, is_future_event,
                city, country_code, participants, activity_type,
                is_valid
            )
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12)
            ON CONFLICT (event_slug) DO UPDATE
            SET url = EXCLUDED.url,
                title = EXCLUDED.title,
                description = EXCLUDED.description,
                start_date = EXCLUDED.start_date,
                end_date = EXCLUDED.end_date,
                is_future_event = EXCLUDED.is_future_event,
                city = EXCLUDED.city,
                country_code = EXCLUDED.country_code,
                participants = EXCLUDED.participants,
                activity_type = EXCLUDED.activity_type,
                is_valid = EXCLUDED.is_valid,
                updated_at = NOW()
            RETURNING *
        """
        return await self.conn.fetchrow(
            query,
            activity_data['event_slug'],
            activity_data['url'],
            activity_data['title'],
            activity_data['description'],
            activity_data['start_date'],
            activity_data['end_date'],
            activity_data['is_future_event'],
            activity_data['city'],
            activity_data['country_code'],
            activity_data['participants'],
            activity_data['activity_type'],
            activity_data['is_valid']
        )
    
    async def insert_activity_section_organisers(
        self, activity_id: int, section_ids: List[int]
    ) -> List[Record]:
        """Etkinlik-şube ilişkilerini ekler.
        
        Args:
            activity_id: Etkinlik ID'si
            section_ids: Şube ID'leri
        
        Returns:
            Eklenen ilişki kayıtları
        """
        query = """
            INSERT INTO activity_section_organisers (activity_id, section_id)
            VALUES ($1, $2)
            ON CONFLICT (activity_id, section_id) DO NOTHING
            RETURNING *
        """
        return await self.conn.fetch(
            query,
            [(activity_id, section_id) for section_id in section_ids]
        )
    
    async def insert_validation_error(
        self,
        section_id: Optional[int],
        activity_event_slug: Optional[str],
        field_name: str,
        error_message: str,
        raw_data: Dict[str, Any],
        scraper_module: str
    ) -> Record:
        """Veri doğrulama hatasını kaydeder.
        
        Args:
            section_id: Şube ID'si (opsiyonel)
            activity_event_slug: Etkinlik slug'ı (opsiyonel)
            field_name: Hatalı alan adı
            error_message: Hata mesajı
            raw_data: Ham veri
            scraper_module: Scraper modülü adı
        
        Returns:
            Eklenen hata kaydı
        """
        query = """
            INSERT INTO validation_errors (
                section_id, activity_event_slug, field_name,
                error_message, raw_data, scraper_module
            )
            VALUES ($1, $2, $3, $4, $5, $6)
            RETURNING *
        """
        return await self.conn.fetchrow(
            query,
            section_id,
            activity_event_slug,
            field_name,
            error_message,
            raw_data,
            scraper_module
        )
    
    async def insert_failed_scrape(
        self,
        url: str,
        section_id: Optional[int],
        scraper_module: str,
        http_status_code: Optional[int],
        error_message: str,
        retry_count: int = 0,
        will_retry: bool = True
    ) -> Record:
        """Başarısız scraping denemesini kaydeder.
        
        Args:
            url: İstek yapılan URL
            section_id: Şube ID'si (opsiyonel)
            scraper_module: Scraper modülü adı
            http_status_code: HTTP durum kodu (opsiyonel)
            error_message: Hata mesajı
            retry_count: Yeniden deneme sayısı
            will_retry: Yeniden denenecek mi
        
        Returns:
            Eklenen hata kaydı
        """
        query = """
            INSERT INTO failed_scrapes (
                url, section_id, scraper_module, http_status_code,
                error_message, retry_count, will_retry
            )
            VALUES ($1, $2, $3, $4, $5, $6, $7)
            RETURNING *
        """
        return await self.conn.fetchrow(
            query,
            url,
            section_id,
            scraper_module,
            http_status_code,
            error_message,
            retry_count,
            will_retry
        )
    
    async def update_scraper_status(
        self,
        scraper_module: str,
        status: str,
        sections_processed: int = 0,
        sections_failed: int = 0,
        error_message: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Record:
        """Scraper durumunu günceller.
        
        Args:
            scraper_module: Scraper modülü adı
            status: Durum (running, completed, failed)
            sections_processed: İşlenen şube sayısı
            sections_failed: Başarısız şube sayısı
            error_message: Hata mesajı (opsiyonel)
            metadata: Ek metadata (opsiyonel)
        
        Returns:
            Güncellenen durum kaydı
        """
        query = """
            INSERT INTO scraper_status (
                scraper_module, status, sections_processed,
                sections_failed, error_message, metadata
            )
            VALUES ($1, $2, $3, $4, $5, $6)
            RETURNING *
        """
        return await self.conn.fetchrow(
            query,
            scraper_module,
            status,
            sections_processed,
            sections_failed,
            error_message,
            metadata
        )
    
    async def get_sections_to_scrape(self, limit: Optional[int] = None) -> List[Record]:
        """Scrape edilecek şubeleri getirir.
        
        Args:
            limit: Maksimum şube sayısı
        
        Returns:
            Şube kayıtları
        """
        query = """
            SELECT *
            FROM sections
            WHERE can_scrape_activities = TRUE
            ORDER BY last_scraped ASC NULLS FIRST
        """
        if limit:
            query += f" LIMIT {limit}"
        return await self.conn.fetch(query)
    
    async def get_section_by_slug(self, activities_platform_slug: str) -> Optional[Record]:
        """Şubeyi activities.esn.org slug'ına göre getirir.
        
        Args:
            activities_platform_slug: Şube slug'ı
        
        Returns:
            Şube kaydı veya None
        """
        query = """
            SELECT *
            FROM sections
            WHERE activities_platform_slug = $1
        """
        return await self.conn.fetchrow(query, activities_platform_slug)
    
    async def get_sections_by_last_scraped(self, limit: Optional[int] = None) -> List[Record]:
        """Son scrape tarihine göre şubeleri getirir.
        
        Args:
            limit: Maksimum şube sayısı
            
        Returns:
            Şube kayıtları, en eski scrape edilenler önce
        """
        query = """
            SELECT *
            FROM sections
            ORDER BY last_scraped ASC NULLS FIRST
        """
        if limit:
            query += f" LIMIT {limit}"
        return await self.conn.fetch(query)

    async def update_section_last_scraped(self, section_id: int) -> Record:
        """Şubenin son scrape tarihini günceller.
        
        Args:
            section_id: Şube ID'si
        
        Returns:
            Güncellenen şube kaydı
        """
        query = """
            UPDATE sections
            SET last_scraped = NOW()
            WHERE id = $1
            RETURNING *
        """
        return await self.conn.fetchrow(query, section_id) 