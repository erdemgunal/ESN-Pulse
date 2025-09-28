"""
Data validation functions for activities.esn.org platform.
"""

import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

async def validate_scraping_data(data: Dict[str, Any]) -> bool:
    """
    Validate scraped data quality.
    
    Args:
        data: Scraped data dictionary
        
    Returns:
        True if data meets quality criteria
    """
    try:
        sections_processed = data.get("sections_processed", 0)
        activities_processed = data.get("activities_processed", 0)
        error_count = len(data.get("errors", []))
        
        # Check if any sections were processed
        if sections_processed == 0:
            logger.warning("No sections processed")
            return False
        
        # Check average activities per section
        if sections_processed > 0:
            avg_activities = activities_processed / sections_processed
            if avg_activities < 5:  # Expect at least 5 activities per section on average
                logger.warning(f"Low activity count: {avg_activities:.1f} per section")
                return False
        
        # Check error rate
        if error_count > sections_processed * 0.2:  # Max 20% error rate
            logger.warning(f"High error rate: {error_count}/{sections_processed}")
            return False
        
        return True
        
    except Exception as e:
        logger.error(f"Data validation failed: {str(e)}")
        return False