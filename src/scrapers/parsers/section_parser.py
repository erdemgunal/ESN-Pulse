"""
Section parsing functions for accounts.esn.org platform.
"""

import json
import logging
from typing import Dict, Any, Optional
from urllib.parse import urljoin
from ...models.section import SectionModel
from ...utils.slug_generator import generate_activities_slug
from ..constants.account_selectors import ACCOUNT_SELECTORS

logger = logging.getLogger(__name__)

def parse_section_link(link, country_code: str, base_url: str) -> Optional[SectionModel]:
    """
    Parse a section link element to extract basic section information.
    
    Args:
        link: BeautifulSoup element containing section link
        country_code: Country code for the section
        base_url: Base URL for constructing full URLs
        
    Returns:
        SectionModel object or None if parsing fails
    """
    try:
        href = link.get('href', '')
        if '/section/' not in href:
            return None
        
        # Extract accounts platform slug
        accounts_slug = href.split('/section/')[-1].strip('/')
        if not accounts_slug:
            return None
        
        name = link.get_text(strip=True)
        if not name:
            return None

        # Generate activities platform slug
        activities_slug = generate_activities_slug(name)
        
        section = SectionModel(
            country_code=country_code.upper(),
            name=name,
            accounts_platform_slug=accounts_slug,
            activities_platform_slug=activities_slug,
            accounts_url=urljoin(base_url, href),
            activities_url=f"https://activities.esn.org/organisation/{activities_slug}"
        )
        
        logger.debug(f"Extracted section: {section.name}")
        return section
        
    except Exception as e:
        logger.warning(f"Failed to extract section from link {link}: {str(e)}")
        return None

def parse_section_details(soup, base_url: str) -> Dict[str, Any]:
    """
    Parse section details from section page.
    
    Args:
        soup: BeautifulSoup object of section page
        base_url: Base URL for constructing full URLs
        
    Returns:
        Dictionary with section details
    """
    details = {}
    
    try:
        # Email
        email_elem = soup.select_one(ACCOUNT_SELECTORS['contact_email'])
        if email_elem:
            details['email'] = email_elem.get_text(strip=True)
        
        # Website
        website_elem = soup.select_one(ACCOUNT_SELECTORS['contact_website'])
        if website_elem:
            details['website'] = website_elem.get('href')
        
        # University name
        university_elem = soup.select_one(ACCOUNT_SELECTORS['university_name'])
        if university_elem:
            details['university_name'] = university_elem.get_text(strip=True)
        
        # Address  
        address_elem = soup.select_one(ACCOUNT_SELECTORS['address'])
        if address_elem:
            address_parts = []
            for span in address_elem.select('span'):
                text = span.get_text(strip=True)
                if text:
                    address_parts.append(text)
            details['address'] = ', '.join(address_parts)
        
        # Coordinates
        coords_elem = soup.select_one(ACCOUNT_SELECTORS['coordinates'])
        if coords_elem:
            try:
                lat = coords_elem.get('data-lat')
                lng = coords_elem.get('data-lng')
                if lat and lng:
                    # Round to 6 decimal places to stay within 9 total digits
                    details['latitude'] = round(float(lat.strip()), 6)
                    details['longitude'] = round(float(lng.strip()), 6)
            except (ValueError, AttributeError):
                pass
        
        # Logo
        logo_elem = soup.select_one(ACCOUNT_SELECTORS['logo'])
        if logo_elem:
            details['logo_url'] = urljoin(base_url, logo_elem.get('src'))
        
        # City
        city_elem = soup.select_one(ACCOUNT_SELECTORS['city'])
        if city_elem:
            details['city'] = city_elem.get_text(strip=True)

        # Social Media
        social_media_links = soup.select(ACCOUNT_SELECTORS['social_media'])
        social_media = {}
        for link in social_media_links:
            title = link.get('title', '').lower()
            if 'profile' in title:
                # Extract platform name from title (e.g., "Facebook profile" -> "facebook")
                platform = title.replace('profile', '').strip()
                if platform:
                    social_media[platform] = link.get('href')
        if social_media:
            details['social_media'] = social_media
        
        return details
        
    except Exception as e:
        logger.warning(f"Failed to extract section details: {str(e)}")
        return details