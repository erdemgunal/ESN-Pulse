import logging
from typing import Dict, Any
from ...models.section import SectionModel

logger = logging.getLogger(__name__)

async def validate_activities_slug(http_client, section: SectionModel) -> bool:
    """
    Validate if activities platform slug is accessible.
    
    Args:
        http_client: HTTP client instance
        section: Section model with activities_platform_slug
        
    Returns:
        True if slug is valid, False otherwise
    """
    if not section.activities_platform_slug:
        section.can_scrape_activities = False
        return False
    
    try:
        is_valid = await http_client.validate_slug_url(
            section.activities_platform_slug,
            "https://activities.esn.org/organisation/{slug}/activities"
        )
        
        section.can_scrape_activities = is_valid
        
        if is_valid:
            logger.debug(f"Activities slug validated: {section.activities_platform_slug}")
        else:
            logger.warning(f"Invalid activities slug: {section.activities_platform_slug}")
            
        return is_valid
        
    except Exception as e:
        logger.error(f"Slug validation error for {section.activities_platform_slug}: {str(e)}")
        section.can_scrape_activities = False
        return False

async def validate_scraping_data(data: Dict[str, Any]) -> bool:
    """
    Validate scraped data quality.
    
    Args:
        data: Scraped data dictionary
        
    Returns:
        True if data meets quality criteria
    """
    try:
        # Check minimum countries
        if data.get("countries_processed", 0) < 40:
            logger.warning("Too few countries processed")
            return False
        
        # Check minimum sections
        if data.get("sections_processed", 0) < 400:
            logger.warning("Too few sections processed")
            return False
        
        # Check validation rate
        processed = data.get("sections_processed", 0)
        validated = data.get("sections_validated", 0)
        
        if processed > 0:
            validation_rate = validated / processed
            if validation_rate < 0.7:  # At least 70% should be valid
                logger.warning(f"Low validation rate: {validation_rate:.2%}")
                return False
        
        # Check error rate
        error_count = len(data.get("errors", []))
        if error_count > processed * 0.1:  # Max 10% errors
            logger.warning(f"Too many errors: {error_count}")
            return False
        
        return True
        
    except Exception as e:
        logger.error(f"Data validation failed: {str(e)}")
        return False