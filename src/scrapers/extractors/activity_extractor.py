import asyncio
import logging
from typing import List, Dict, Any

from ...models.activity import ActivityModel
from ...config import settings
from ..parsers.activity_parser import (
    find_last_page_number, 
    parse_activity_from_listing, 
    parse_activity_details,
    create_chunks
)

logger = logging.getLogger(__name__)

async def extract_activities_for_section(
    http_client,
    activities_slug: str,
    base_url: str
) -> List[Dict[str, Any]]:
    if not activities_slug:
        logger.warning("No activities slug provided")
        return []
    
    activities_url = f"{base_url}/organisation/{activities_slug}/activities"
    logger.info(f"Extracting activities from: {activities_url}")
    
    try:
        all_activities = []
        
        # Step 1: Get first page to analyze pagination
        first_page_url = f"{activities_url}?page=0"
        logger.info(f"Fetching first page for pagination analysis: {first_page_url}")
        
        content = await http_client.get_page_content(first_page_url)
        soup = await http_client.parse_html(content, first_page_url)
        
        # Find total pages
        last_page = find_last_page_number(soup)
        total_pages = last_page + 1  # Convert from 0-indexed to count
        logger.info(f"Found {total_pages} total pages (0-{last_page})")
        
        # Step 2: Create chunks for parallel processing
        chunks = create_chunks(last_page, chunk_size=settings.PAGINATION_CHUNK_SIZE)
        
        # For debug purposes, let's process sequentially rather than using Celery
        # In production, this would use Celery for parallel processing
        for chunk_start, chunk_end in chunks:
            logger.info(f"Processing chunk: pages {chunk_start}-{chunk_end}")
            
            chunk_activities = await extract_activities_chunk(
                http_client, 
                activities_url, 
                chunk_start, 
                chunk_end,
                base_url
            )
            
            all_activities.extend(chunk_activities)
            logger.info(f"Chunk {chunk_start}-{chunk_end} yielded {len(chunk_activities)} activities")
        
        logger.info(f"Total activities extracted: {len(all_activities)}")
        return all_activities
        
    except Exception as e:
        logger.error(f"Failed to extract activities for {activities_slug}: {str(e)}")
        return []

async def extract_activities_chunk(
    http_client,
    activities_url: str,
    start_page: int,
    end_page: int,
    base_url: str
) -> List[Dict[str, Any]]:
    chunk_activities = []
    
    try:
        for page_num in range(start_page, end_page + 1):
            logger.info(f"Processing page {page_num}")
            
            page_url = f"{activities_url}?page={page_num}"
            content = await http_client.get_page_content(page_url)
            soup = await http_client.parse_html(content, page_url)
            
            # Extract activities from this page
            page_activities = await extract_activities_from_page(
                http_client, soup, base_url
            )
            
            chunk_activities.extend(page_activities)
            logger.info(f"Page {page_num} yielded {len(page_activities)} activities")
            
            # Add small delay between pages to be respectful
            await asyncio.sleep(settings.SCRAPING_DELAY)
        
        return chunk_activities
        
    except Exception as e:
        logger.error(f"Failed to extract activities chunk {start_page}-{end_page}: {str(e)}")
        return chunk_activities

async def extract_activities_from_page(
    http_client,
    soup,
    base_url: str
) -> List[Dict[str, Any]]:
    page_activities = []
    
    try:
        # Find activity articles (both physical and online)
        activity_articles = soup.select('article.activities-mini-preview')
        logger.debug(f"Found {len(activity_articles)} activity articles on page")
        
        for article in activity_articles:
            try:
                # Parse basic URL info from listing
                url_info = parse_activity_from_listing(article, base_url)
                if not url_info:
                    continue
                
                # Get detailed info from activity page
                activity_url = url_info['url']
                event_slug = url_info['event_slug']
                
                logger.debug(f"Fetching details for: {event_slug}")
                
                detail_content = await http_client.get_page_content(activity_url)
                detail_soup = await http_client.parse_html(detail_content, activity_url)
                
                # Parse detailed information and get ActivityModel
                activity_model = parse_activity_details(detail_soup, activity_url, event_slug)
                
                if activity_model:
                    # Convert to dict for now (can keep as model if needed)
                    activity_data = activity_model.dict()
                    page_activities.append(activity_data)
                    
                # Add delay between detail requests
                await asyncio.sleep(settings.SCRAPING_DELAY)
                
            except Exception as e:
                logger.warning(f"Failed to extract activity details: {str(e)}")
                continue
        
        return page_activities
        
    except Exception as e:
        logger.error(f"Failed to extract activities from page: {str(e)}")
        return page_activities

async def validate_activities_data(activities: List[Dict[str, Any]]) -> List[ActivityModel]:
    validated_activities = []
    
    for activity_data in activities:
        try:
            # Convert to ActivityModel for validation
            activity = ActivityModel(**activity_data)
            validated_activities.append(activity)
            
        except Exception as e:
            logger.warning(f"Activity validation failed for {activity_data.get('title', 'Unknown')}: {str(e)}")
            continue
    
    logger.info(f"Validated {len(validated_activities)} out of {len(activities)} activities")
    return validated_activities