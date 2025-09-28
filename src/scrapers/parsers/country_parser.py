"""
Country parsing functions for accounts.esn.org platform.
"""

import logging
from typing import Optional
from urllib.parse import urljoin
from ...models.country import CountryModel
from ..constants.account_selectors import ACCOUNT_SELECTORS

logger = logging.getLogger(__name__)

def parse_country_link(link, base_url: str) -> Optional[CountryModel]:
    """
    Parse a country link element to extract country information.
    
    Args:
        link: BeautifulSoup element containing country link
        base_url: Base URL for constructing full URLs
        
    Returns:
        CountryModel object or None if parsing fails
    """
    try:
        href = link.get('href', '')
        if '/country/' not in href:
            logger.warning(f"Skipping invalid link: {href}")
            return None
            
        # Extract country code from URL
        country_code = href.split('/country/')[-1].strip('/')
        if not country_code or len(country_code) != 2:
            logger.warning(f"Invalid country code: {country_code}")
            return None
            
        name = link.get_text(strip=True)
        if not name:
            logger.warning(f"Empty country name for code: {country_code}")
            return None
        
        country = CountryModel(
            country_code=country_code.upper(),
            name=name,
            slug=country_code.lower(),
            url=urljoin(base_url, href),
            section_count=0  # Will be updated later
        )
        
        logger.debug(f"Extracted country: {country.name} ({country.country_code})")
        return country
        
    except Exception as e:
        logger.warning(f"Failed to extract country from link {link}: {str(e)}")
        return None