"""
ESN PULSE Activities Tasks

Bu modül, activities.esn.org platformundan veri çekme görevlerini içerir.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Optional

from celery import shared_task
from celery.utils.log import get_task_logger

from src.database.connection import get_db_connection
from src.scrapers.activities_statistics_scraper import ActivitiesAndStatisticsScraper

logger = get_task_logger(__name__)

@shared_task(
    name='src.tasks.activities_tasks.run_activities_scraper',
    bind=True,
    max_retries=3,
    default_retry_delay=300,  # 5 dakika
    time_limit=3600,  # 1 saat
    soft_time_limit=3300,  # 55 dakika
)
def run_activities_scraper(self, section_slug: Optional[str] = None):
    """ActivitiesAndStatisticsScraper'ı çalıştıran Celery görevi.
    
    Bu görev:
    1. activities.esn.org'dan etkinlik ve istatistik verilerini çeker
    2. Verileri veritabanına kaydeder
    
    Args:
        section_slug: Belirli bir şube için scraping yapılacaksa, o şubenin slug'ı
    """
    try:
        # Asenkron scraper'ı çalıştır
        asyncio.run(_run_activities_scraper(section_slug))
        
        logger.info("✅ ActivitiesAndStatisticsScraper başarıyla tamamlandı")
        return True
    except Exception as e:
        logger.error(f"❌ ActivitiesAndStatisticsScraper hatası: {str(e)}")
        # Görevi yeniden dene
        raise self.retry(exc=e)

async def _run_activities_scraper(section_slug: Optional[str] = None):
    """ActivitiesAndStatisticsScraper'ın asenkron çalıştırma fonksiyonu."""
    async with get_db_connection() as conn:
        scraper = ActivitiesAndStatisticsScraper(conn)
        if section_slug:
            await scraper.run_for_section(section_slug)
        else:
            await scraper.run() 