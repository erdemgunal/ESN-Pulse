"""
ESN PULSE Activities Chunk Task

Bu modül, activities.esn.org platformundan veri çekme görevlerini chunk'lar halinde işler.
"""

import logging
from typing import Dict, Any, List, Optional
from celery import shared_task
from celery.utils.log import get_task_logger

from ..scrapers.base_scraper import BaseScraper
from ..scrapers.extractors.activity_extractor import extract_activities_chunk

logger = get_task_logger(__name__)

@shared_task(
    bind=True,
    max_retries=3,
    default_retry_delay=60,  # 1 minute delay between retries
    autoretry_for=(Exception,),
    retry_backoff=True,
    retry_backoff_max=600,  # Maximum delay of 10 minutes
    retry_jitter=True
)
def scrape_activities_chunk(
    self,
    section_slug: str,
    start_page: int,
    end_page: int,
    base_url: str = "https://activities.esn.org"
) -> List[Dict[str, Any]]:
    """
    Celery task to scrape a chunk of activities pages for a given section.
    
    Args:
        section_slug: The section's activities platform slug
        start_page: Starting page number (inclusive)
        end_page: Ending page number (inclusive)
        base_url: Base URL for the activities platform
        
    Returns:
        List of activity dictionaries
    """
    logger.info(f"Starting chunk task for {section_slug} pages {start_page}-{end_page}")
    
    try:
        # Create HTTP client
        scraper = BaseScraper()
        activities_url = f"{base_url}/organisation/{section_slug}/activities"
        
        # Extract activities for this chunk
        chunk_activities = extract_activities_chunk(
            scraper,
            activities_url,
            start_page,
            end_page,
            base_url
        )
        
        logger.info(f"Successfully extracted {len(chunk_activities)} activities from chunk {start_page}-{end_page}")
        return chunk_activities
            
    except Exception as e:
        logger.error(f"Failed to process chunk {start_page}-{end_page} for {section_slug}: {str(e)}")
        raise  # Celery will handle retry logic based on decorator settings