import logging
import asyncio
from typing import Dict, Any, Optional, List
from datetime import datetime
from celery import group

from ..database.operations import DatabaseOperations
from .base_scraper import BaseScraper
from .extractors.statistics_extractor import extract_section_statistics
from .extractors.activity_extractor import extract_activities_for_section
from .validators.data_validator import validate_scraping_data
from .parsers.activity_parser import find_last_page_number, create_chunks
from ..tasks.activities_chunk_task import scrape_activities_chunk
from ..config import settings

logger = logging.getLogger(__name__)

class ActivitiesAndStatisticsScraper(BaseScraper):
    def __init__(self):
        super().__init__()
        self.base_url = "https://activities.esn.org"
        self.db_ops: Optional[DatabaseOperations] = None
    
    async def __aenter__(self):
        await super().__aenter__()
        self.db_ops = DatabaseOperations()
        await self.db_ops.__aenter__()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.db_ops:
            await self.db_ops.__aexit__(exc_type, exc_val, exc_tb)
        await super().__aexit__(exc_type, exc_val, exc_tb)
    
    async def scrape(
        self, 
        section_slug: Optional[str] = None,
        max_sections: Optional[int] = None
    ) -> Dict[str, Any]:
        async with self as scraper:
            logger.info("Starting ActivitiesAndStatisticsScraper...")
            
            results = {
                "sections_processed": 0,
                "activities_processed": 0,
                "statistics_processed": 0,
                "errors": [],
                "start_time": datetime.now(),
                "end_time": None
            }
            
            try:
                # Get sections to process
                if section_slug:
                    sections = [await self.db_ops.get_section_by_slug(section_slug)]
                    if not sections[0]:
                        raise ValueError(f"Section not found: {section_slug}")
                else:
                    sections = await self.db_ops.get_sections_to_scrape(
                        limit=max_sections
                    )
                
                logger.info(f"Processing {len(sections)} sections")
                
                print(sections)
                print(f"Number of sections: {len(sections)}")
                print(f"Type of sections: {type(sections)}")
                
                # Process each section
                for i, section in enumerate(sections):
                    print(f"Processing section {i}: {section}")
                    logger.info(f"Starting to process section: {section['name']}")
                    try:
                        logger.info(f"Starting to process section: {section['name']}")
                        section_results = await self.process_section_parallel(section)
                        
                        results["sections_processed"] += 1
                        results["activities_processed"] += section_results.get("activities_count", 0)
                        results["statistics_processed"] += section_results.get("statistics_count", 0)
                        
                        logger.info(f"Processed section {section['name']}: "
                                f"{section_results.get('activities_count', 0)} activities, "
                                f"{section_results.get('statistics_count', 0)} statistics")
                    
                    except Exception as e:
                        error_msg = f"Failed to process section {section['name']}: {str(e)}"
                        logger.error(error_msg)
                        logger.error(f"Exception details: {type(e).__name__}: {str(e)}")
                        import traceback
                        logger.error(f"Traceback: {traceback.format_exc()}")
                        results["errors"].append(error_msg)
                
                results["end_time"] = datetime.now()
                duration = (results["end_time"] - results["start_time"]).total_seconds()
                
                logger.info(f"ActivitiesAndStatisticsScraper completed in {duration:.1f}s. "
                           f"Processed {results['sections_processed']} sections, "
                           f"{results['activities_processed']} activities")
                
                # Validate results
                if not await self.validate_data(results):
                    logger.warning("Data validation failed")
                
            except Exception as e:
                logger.error(f"ActivitiesAndStatisticsScraper failed: {str(e)}")
                results["errors"].append(str(e))
                raise
                
            return results
    
    async def process_section_parallel(self, section) -> Dict[str, Any]:
        """Process a section's activities and statistics in parallel using Celery workers."""
        activities_count = 0
        statistics_count = 0
        all_activities = []
        
        try:
            # 1. Get first page to analyze pagination
            activities_url = f"{self.base_url}/organisation/{section['activities_platform_slug']}/activities"
            first_page_url = f"{activities_url}?page=0"
            
            logger.info(f"Analyzing pagination for section {section['name']}")
            content = await self.get_page_content(first_page_url)
            soup = await self.parse_html(content, first_page_url)
            
            # Find total pages and create chunks
            last_page = find_last_page_number(soup)
            chunks = create_chunks(last_page, chunk_size=settings.PAGINATION_CHUNK_SIZE)
            
            logger.info(f"Found {last_page + 1} pages, created {len(chunks)} chunks")
            
            # 2. Create parallel tasks for each chunk
            tasks = []
            for chunk_start, chunk_end in chunks:
                task = scrape_activities_chunk.delay(
                    section['activities_platform_slug'],
                    chunk_start,
                    chunk_end,
                    self.base_url
                )
                tasks.append(task)
            
            # 3. Wait for all tasks to complete
            logger.info(f"Waiting for {len(tasks)} chunk tasks to complete")
            
            for task in tasks:
                try:
                    chunk_activities = task.get(timeout=180)  # 3 minutes timeout per chunk
                    all_activities.extend(chunk_activities)
                    activities_count += len(chunk_activities)
                    logger.info(f"Received {len(chunk_activities)} activities from chunk task")
                    
                except Exception as e:
                    error_msg = f"Chunk task failed: {str(e)}"
                    logger.error(error_msg)
                    # Continue with other chunks even if one fails
            
            # 4. Process statistics (can run in parallel with activities)
            try:
                statistics = await extract_section_statistics(
                    self,
                    section['activities_platform_slug'],
                    self.base_url
                )
                
                if statistics:
                    # await self.db_ops.upsert_section_statistics(statistics, section['id'])
                    statistics_count = 1
                    print(statistics)
                    
            except Exception as e:
                logger.error(f"Failed to process statistics for {section['name']}: {str(e)}")
            
            # Print activities for now (later will be saved to DB)
            for activity in all_activities:
                print(activity)
                print()
            
            # # 5. Update last_scraped timestamp
            # await self.db_ops.update_section_last_scraped(section['id'])
            
            return {
                "activities_count": activities_count,
                "statistics_count": statistics_count
            }
            
        except Exception as e:
            logger.error(f"Failed to process section {section['name']} in parallel: {str(e)}")
            raise

    async def validate_data(self, data: Dict[str, Any]) -> bool:
        return await validate_scraping_data(data)