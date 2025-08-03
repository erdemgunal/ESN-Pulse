"""
ESN PULSE Accounts Tasks

Bu modül, accounts.esn.org platformundan veri çekme görevlerini içerir.
"""

import asyncio
import logging
from datetime import datetime, timedelta

from celery import shared_task
from celery.utils.log import get_task_logger

from src.database.connection import get_db_connection
from src.scrapers.accounts_scraper import AccountsScraper

logger = get_task_logger(__name__)

@shared_task(
    name='src.tasks.accounts_tasks.run_accounts_scraper',
    bind=True,
    max_retries=3,
    default_retry_delay=300,  # 5 dakika
    time_limit=3600,  # 1 saat
    soft_time_limit=3300,  # 55 dakika
)
def run_accounts_scraper(self):
    """AccountsScraper'ı çalıştıran Celery görevi.
    
    Bu görev:
    1. accounts.esn.org'dan tüm ülke ve şube bilgilerini çeker
    2. Verileri veritabanına kaydeder
    3. Her şube için activities.esn.org slug'ını doğrular
    """
    try:
        # Asenkron scraper'ı çalıştır
        asyncio.run(_run_accounts_scraper())
        
        logger.info("✅ AccountsScraper başarıyla tamamlandı")
        return True
    except Exception as e:
        logger.error(f"❌ AccountsScraper hatası: {str(e)}")
        # Görevi yeniden dene
        raise self.retry(exc=e)

async def _run_accounts_scraper():
    """AccountsScraper'ın asenkron çalıştırma fonksiyonu."""
    async with get_db_connection() as conn:
        scraper = AccountsScraper(conn)
        await scraper.run() 