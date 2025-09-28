"""
Country extraction functions for accounts.esn.org platform.
"""

import logging
from typing import List
from ...models.country import CountryModel
from ..constants.account_selectors import ACCOUNT_SELECTORS
from ..parsers.country_parser import parse_country_link

logger = logging.getLogger(__name__)

async def extract_countries(http_client, base_url: str) -> List[CountryModel]:
    """
    Extract all countries from accounts.esn.org main page.
    
    Args:
        http_client: HTTP client instance
        base_url: Base URL for the platform
        
    Returns:
        List of CountryModel objects
    """
    url = f"{base_url}/"
    logger.info(f"Fetching countries from: {url}")
    
    try:
        logger.debug(f"Initializing HTTP client for: {url}")
        await http_client._initialize_session()
        
        logger.debug(f"Getting page content from: {url}")
        content = await http_client.get_page_content(url)
        
        logger.debug(f"Parsing HTML from: {url}")
        soup = await http_client.parse_html(content, url)
        
        countries = []
        country_links = soup.select(ACCOUNT_SELECTORS['country_links'])
        logger.info(f"Found {len(country_links)} country links")
        
        for link in country_links:
            country = parse_country_link(link, base_url)
            if country:
                countries.append(country)
        
        logger.info(f"Total countries extracted: {len(countries)}")
        return countries
        
    except Exception as e:
        logger.error(f"Failed to extract countries: {str(e)}")
        return []