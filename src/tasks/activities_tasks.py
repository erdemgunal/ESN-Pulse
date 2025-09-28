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
    """Scheduled task for running activities scraper.
    
    Args:
        section_slug: Optional section slug to scrape specific section
    """
    try:
        logger.info(f"Starting activities scraper for section: {section_slug or 'all'}")
        return True
    except Exception as e:
        logger.error(f"Error in activities scraper: {str(e)}")
        raise self.retry(exc=e) 