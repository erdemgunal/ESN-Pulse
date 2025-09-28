"""
Section extraction functions for accounts.esn.org platform.
"""

import logging
from typing import List, Dict, Any
from ...models.section import SectionModel
from ..constants.account_selectors import ACCOUNT_SELECTORS
from ..parsers.section_parser import parse_section_link, parse_section_details

logger = logging.getLogger(__name__)

async def extract_sections_for_country(
    http_client,
    country_code: str,
    base_url: str
) -> List[SectionModel]:
    """
    Extract all sections for a specific country.
    
    Args:
        http_client: HTTP client instance
        country_code: Country code (e.g., 'TR', 'DE')
        base_url: Base URL for the platform
        
    Returns:
        List of SectionModel objects
    """
    url = f"{base_url}/country/{country_code.lower()}"
    logger.info(f"Fetching sections for {country_code} from: {url}")
    
    try:
        content = await http_client.get_page_content(url)
        soup = await http_client.parse_html(content, url)

        sections = []
        section_links = soup.select(ACCOUNT_SELECTORS['section_links'])
        section_links = [s for s in section_links if s.get('href') != '']
        
        logger.info(f"Found {len(section_links)} unique sections")
        
        for link in section_links:
            # if link.get('href') == '/section/tr-ista-mar':
            section = parse_section_link(link, country_code, base_url)
            # Get additional details from section page
            section_details = await extract_section_details(
                http_client,
                section.accounts_platform_slug,
                base_url
            )

            # Update section with details
            for key, value in section_details.items():
                setattr(section, key, value)
            sections.append(section)
        
        return sections
        
    except Exception as e:
        logger.error(f"Failed to extract sections for country {country_code}: {str(e)}")
        return []

async def extract_section_details(
    http_client,
    accounts_slug: str,
    base_url: str
) -> Dict[str, Any]:
    """
    Extract detailed information for a specific section.
    
    Args:
        http_client: HTTP client instance
        accounts_slug: Section slug on accounts platform
        base_url: Base URL for the platform
        
    Returns:
        Dictionary with section details
    """
    url = f"{base_url}/section/{accounts_slug}"
    logger.info(f"Fetching section details from: {url}")
    
    try:
        content = await http_client.get_page_content(url)
        soup = await http_client.parse_html(content, url)
        
        return parse_section_details(soup, base_url)
        
    except Exception as e:
        logger.warning(f"Failed to extract details for section {accounts_slug}: {str(e)}")
        return {}