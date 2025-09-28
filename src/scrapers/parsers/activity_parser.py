import logging
import re
from typing import Dict, Any, Optional, List
from urllib.parse import urljoin
from datetime import date, datetime
from bs4 import BeautifulSoup, Tag

from ...models.activity import ActivityModel
from ..constants.country_mappings import COUNTRY_MAPPING
from ..constants.activity_selectors import ACTIVITY_SELECTORS

logger = logging.getLogger(__name__)

def get_text_safely(element, default: str = "") -> str:
    """Safely extract text from a BeautifulSoup element."""
    if element:
        return element.get_text(strip=True)
    return default

def parse_date_safely(date_str: str) -> Dict[str, Optional[date]]:
    result = {'start_date': None, 'end_date': None, 'is_future_event': False}
    
    if not date_str:
        return result
    
    try:
        # Common date formats to try
        date_formats = [
            "%Y-%m-%dT%H:%M:%SZ",
            "%d/%m/%Y",
            "%d %b %Y",
            "%d-%m-%Y",
            "%Y-%m-%d",
            "%B %d, %Y",
        ]
        
        # Try to parse as single date first
        for fmt in date_formats:
            try:
                parsed_date = datetime.strptime(date_str, fmt).date()
                result['start_date'] = parsed_date
                result['end_date'] = parsed_date
                result['is_future_event'] = parsed_date > date.today()
                return result
            except ValueError:
                continue
        
        logger.warning(f"Could not parse date string: {date_str}")
        
    except Exception as e:
        logger.warning(f"Error parsing date '{date_str}': {str(e)}")
    
    return result

def find_last_page_number(soup: BeautifulSoup) -> int:
    try:
        last_page_link = soup.select_one(ACTIVITY_SELECTORS["last_page"])
        # last_page = 0
        if last_page_link:
            last_page = int(last_page_link['href'].split('=')[-1])
        else:
            last_page = 0  # If no pagination, assume only one page
        
        return last_page
        
    except Exception as e:
        logger.warning(f"Failed to find last page number: {str(e)}")
        return 0

def parse_activity_from_listing(article: Tag, base_url: str) -> Optional[Dict[str, str]]:
    try:
        # Get title link which contains the URL
        title_elem = article.select_one(ACTIVITY_SELECTORS["activity_card_title"])
        
        if not title_elem:
            logger.warning("No title link found in activity listing")
            return None
        
        href = title_elem.get('href', '')
        if not href:
            logger.warning("No href found in title link")
            return None
        
        if '/activity/' not in href:
            logger.warning(f"Invalid activity URL: {href}")
            return None
        
        # Extract event slug from URL
        event_slug = href.split('/activity/')[-1].strip('/')
        
        return {
            'url': urljoin(base_url, href),
            'event_slug': event_slug
        }
        
    except Exception as e:
        logger.warning(f"Failed to parse activity from listing: {str(e)}")
        return None

def parse_activity_details(soup: BeautifulSoup, url: str, event_slug: str) -> Optional[ActivityModel]:
    try:
        # Basic event information
        title_elem = soup.select_one(ACTIVITY_SELECTORS["title"]["primary"])
        if not title_elem:
            title_elem = soup.select_one(ACTIVITY_SELECTORS["title"]["fallback"])
        title = get_text_safely(title_elem, "Unknown Activity")
        
        # Description - try multiple selectors
        description = "No description available"
        for selector in ACTIVITY_SELECTORS["description"]:
            description_element = soup.select_one(selector)
            if description_element:
                description = description_element.get_text(separator=' ', strip=True)
                break

        # Dates - try multiple selectors
        date_elements = soup.select(ACTIVITY_SELECTORS["dates"]["primary"])
        if not date_elements:
            date_elements = soup.select(ACTIVITY_SELECTORS["dates"]["fallback"])
        
        start_date = None
        end_date = None
        is_future_event = False
        
        if date_elements:
            start_date_str = get_text_safely(date_elements[0])
            date_info = parse_date_safely(start_date_str)
            start_date = date_info['start_date']
            end_date = date_info['end_date']
            is_future_event = date_info['is_future_event']
            
            if len(date_elements) > 1:
                end_date_str = get_text_safely(date_elements[1])
                end_date_info = parse_date_safely(end_date_str)
                if end_date_info['start_date']:
                    end_date = end_date_info['start_date']
        
        # Default to today if no date found
        if not start_date:
            start_date = date.today()
            end_date = date.today()
            is_future_event = False

        # Location - try multiple selectors
        city = "Unknown"
        country_code = "XX"
        location_elements = []
        
        for selector in ACTIVITY_SELECTORS["location"]:
            location_elements = soup.select(selector)
            if location_elements:
                break
                
        if location_elements:
            city = get_text_safely(location_elements[0]) or "Unknown"
            if len(location_elements) > 1:
                country_name = get_text_safely(location_elements[1])
                country_code = COUNTRY_MAPPING.get(country_name, 'XX')

        # Participants
        participants_element = soup.select_one(ACTIVITY_SELECTORS["participants"]["primary"])
        if not participants_element:
            participants_element = soup.select_one(ACTIVITY_SELECTORS["participants"]["fallback"])
            
        participants = 0
        if participants_element:
            participants_text = get_text_safely(participants_element)
            try:
                participants = int(re.sub(r'[^\d]', '', participants_text))
            except (ValueError, TypeError):
                participants = 0

        # Activity type
        activity_type_elem = soup.select_one(ACTIVITY_SELECTORS["activity_type"]["primary"])
        if not activity_type_elem:
            activity_type_elem = soup.select_one(ACTIVITY_SELECTORS["activity_type"]["fallback"])
        activity_type = get_text_safely(activity_type_elem)

        # Lists of related information
        organiser_elems = soup.select(ACTIVITY_SELECTORS["organisers"]["primary"])
        if not organiser_elems:
            organiser_elems = soup.select(ACTIVITY_SELECTORS["organisers"]["fallback"])
        organisers = [get_text_safely(a) for a in organiser_elems if get_text_safely(a)]
        
        cause_elems = soup.select(ACTIVITY_SELECTORS["causes"]["primary"])
        if not cause_elems:
            cause_elems = soup.select(ACTIVITY_SELECTORS["causes"]["fallback"])
        causes = list(set([get_text_safely(a) for a in cause_elems if get_text_safely(a)]))

        # SDGs
        sdg_elements = soup.select(ACTIVITY_SELECTORS["sdgs"])
        sdgs = []
        for img in sdg_elements:
            alt_text = img.get('alt', '')
            # Try different patterns: "Goal 3", "SDG 3", etc.
            match = re.search(r'(?:Goal|SDG)\s+(\d+)', alt_text, re.IGNORECASE)
            if match:
                try:
                    sdg_num = int(match.group(1))
                    if 1 <= sdg_num <= 17:
                        sdgs.append(sdg_num)
                except ValueError:
                    continue
        sdgs = sorted(list(set(sdgs)))  # Remove duplicates and sort

        # Objectives
        objective_elems = soup.select(ACTIVITY_SELECTORS["objectives"])
        objectives = list(set([get_text_safely(s) for s in objective_elems if get_text_safely(s)]))

        # Activity Goal
        activity_goal = None
        for selector in ACTIVITY_SELECTORS["activity_goal"]:
            activity_goal_elem = soup.select_one(selector)
            if activity_goal_elem:
                # Check if there are list items
                list_items = activity_goal_elem.find_all('li')
                if list_items:
                    # If there are list items, join them with newlines
                    activity_goal = '\n'.join([item.get_text(strip=True) for item in list_items if item.get_text(strip=True)])
                else:
                    # If no list items, get text normally
                    activity_goal = get_text_safely(activity_goal_elem)
                break

        # Create ActivityModel
        activity = ActivityModel(
            event_slug=event_slug,
            url=url,
            title=title,
            description=description,
            start_date=start_date,
            end_date=end_date,
            city=city,
            country_code=country_code,
            participants=participants,
            activity_type=activity_type if activity_type else None,
            activity_goal=activity_goal if activity_goal else None,
            is_future_event=is_future_event,
            organisers=organisers,
            causes=causes,
            sdgs=sdgs,
            objectives=objectives
        )

        logger.debug(f"Successfully created ActivityModel for: {title}")
        return activity
        
    except Exception as e:
        logger.error(f"Failed to parse activity details for {event_slug}: {str(e)}")
        return None

def create_chunks(last_page: int, chunk_size: int = 5) -> List[tuple]:
    chunks = [(i, min(i + chunk_size - 1, last_page)) for i in range(0, last_page + 1, chunk_size)]
    
    logger.debug(f"Created {len(chunks)} chunks for {last_page + 1} pages")
    return chunks