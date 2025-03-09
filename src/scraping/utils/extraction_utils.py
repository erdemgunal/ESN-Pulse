import re
import html
from typing import Dict, Any, Tuple, Union, TypeVar, Optional

from bs4 import BeautifulSoup

# Add a generic type for the ensure_value function
T = TypeVar('T')

def ensure_value(value: Optional[T], default: T, field_name: str = "") -> T:
    """
    Ensures a value is not empty, providing a default if it is
    
    Args:
        value: Value to check
        default: Default value to use if empty
        field_name: Name of field for logging (optional)
        
    Returns:
        Original value or default if empty
    """
    # Check for None
    if value is None:
        return default
        
    # Check for empty strings
    if isinstance(value, str) and not value.strip():
        return default
        
    # Check for empty collections
    if hasattr(value, '__len__') and len(value) == 0:
        return default
        
    # Special check for "not found" placeholder strings
    if isinstance(value, str) and any(x in value.lower() for x in ["not found", "unknown"]):
        return default
        
    return value

def ensure_integer(value: Union[str, int, float]) -> int:
    """
    Ensures a value is converted to an integer
    
    Args:
        value: Value to convert to integer
        
    Returns:
        Integer value or 0 if conversion fails
    """
    if isinstance(value, int):
        return value
    
    if isinstance(value, float):
        return int(value)
    
    if isinstance(value, str):
        # Remove all non-numeric characters
        numeric_str = re.sub(r'[^0-9]', '', value)
        if numeric_str:
            try:
                return int(numeric_str)
            except ValueError:
                pass
    
    return 0  # Default if conversion fails

def extract_statistic(statistics: Dict[str, Any], key: str) -> Dict[str, Any]:
    """
    Extract a specific statistic from the JSON data
    
    Args:
        statistics: Dictionary containing statistics data
        key: Key for the statistic (e.g., 'total_activities')
        
    Returns:
        Dictionary with extracted statistic data
    """
    data = statistics.get(key, {})
    result = {}
    
    if 'values' in data:
        for item in data['values']:
            if isinstance(item, list) and len(item) >= 2:
                # Ensure the second item (count) is an integer
                result[item[0]] = ensure_integer(item[1])
    
    if 'total_num' in data:
        # Ensure total_num is an integer
        result['total'] = ensure_integer(data['total_num'])
    
    return result

def extract_causes(statistics: Dict[str, Any], key: str) -> Dict[str, int]:
    """
    Extract activity causes and their counts
    
    Args:
        statistics: Dictionary containing statistics data
        key: Key for the causes (e.g., 'total_causes')
        
    Returns:
        Dictionary with cause names as keys and counts as values
    """
    causes = {}
    data = statistics.get(key, {})
    
    if 'values' in data:
        for item in data['values']:
            if isinstance(item, list) and len(item) >= 2:
                causes[item[0]] = ensure_integer(item[1])
    
    return causes

def extract_types(statistics: Dict[str, Any], key: str) -> Dict[str, int]:
    """
    Extract activity types and their counts
    
    Args:
        statistics: Dictionary containing statistics data
        key: Key for the types (e.g., 'physical_types')
        
    Returns:
        Dictionary with type names as keys and counts as values
    """
    types = {}
    data = statistics.get(key, {})
    
    if 'values' in data:
        for item in data['values']:
            if isinstance(item, list) and len(item) >= 2:
                types[item[0]] = ensure_integer(item[1])
    
    return types

def extract_statistics(soup: BeautifulSoup) -> Dict[str, Union[str, int]]:
    """
    Extract statistics from the organization page
    
    Args:
        soup: BeautifulSoup object of the organization page
        
    Returns:
        Dictionary with statistic names and values
    """
    statistics = {}
    
    try:
        stats_container = soup.find('div', class_='organisation--block-counters')
        if stats_container:
            for stat in stats_container.find_all('div', class_='count-container'):
                try:
                    stat_name = clean_text(stat.find('h3').text)
                    stat_value_text = clean_text(stat.find('span').text)
                    
                    # Convert to integer if it's numeric
                    if re.match(r'^\d+$', stat_value_text.replace(',', '').replace('.', '')):
                        stat_value = ensure_integer(stat_value_text)
                    else:
                        stat_value = stat_value_text
                        
                    statistics[stat_value] = stat_name
                except (AttributeError, TypeError):
                    continue
    except (AttributeError, TypeError):
        pass
        
    return statistics

def clean_html_text(text: str, preserve_special_chars: bool = True) -> str:
    """
    Clean text by removing HTML tags, decoding HTML entities, and handling special characters
    
    Args:
        text: String to clean
        preserve_special_chars: Whether to preserve punctuation/special characters
        
    Returns:
        Cleaned string
    """
    if not text:
        return text
    
    # Decode HTML entities like &amp; or &gt;
    text = html.unescape(text)
    
    # Remove any HTML tags that might be present
    text = re.sub(r'<[^>]+>', ' ', text)
    
    # Replace escape sequences with spaces
    text = text.replace('\n', ' ').replace('\t', ' ').replace('\r', ' ')
    
    # Replace multiple whitespaces with a single space
    text = re.sub(r'\s+', ' ', text)
    
    # Remove special characters if needed
    if not preserve_special_chars:
        text = re.sub(r'[^\w\s]', '', text)
    
    # Final trim
    return text.strip()

# Update the original clean_text to use the new HTML-aware cleaner
def clean_text(text: str) -> str:
    """
    Clean text by removing special characters, excess whitespace, and escape sequences
    
    Args:
        text: String to clean
        
    Returns:
        Cleaned string
    """
    return clean_html_text(text, preserve_special_chars=False)

def clean_date_text(text: str) -> str:
    """
    Clean date text while preserving important date characters like /, -, :
    
    Args:
        text: Date string to clean
        
    Returns:
        Cleaned date string suitable for database insertion
    """
    if not text:
        return text
        
    # Replace escape sequences with spaces
    text = text.replace('\n', ' ').replace('\t', ' ').replace('\r', ' ')
    
    # Replace multiple whitespaces with a single space
    text = re.sub(r'\s+', ' ', text)
    
    # Final trim
    return text.strip()

def extract_activity_date(soup: BeautifulSoup) -> str:
    """Extract activity date handling multiple possible formats"""
    try:
        # Try original method first
        activity_date = clean_date_text(soup.find('div', class_='highlight-dates-single').find('span').text)
        return ensure_value(activity_date, "Date unknown", "activity_date")
    except (AttributeError, TypeError):
        try:
            # Alternative format with multiple spans
            date_spans = soup.find('div', class_='highlight-data-text').find_all('span')
            if date_spans:
                joined_date = ' - '.join([clean_date_text(span.text) for span in date_spans])
                return ensure_value(joined_date, "Date unknown", "activity_date")
        except (AttributeError, TypeError):
            pass
    return "Date unknown"

def extract_location(soup: BeautifulSoup) -> Tuple[str, str]:
    """Extract activity location handling both online and physical activities"""
    # Check if this is an online activity by looking for the online portal icon
    online_icon = soup.find('img', {"src": re.compile(r'icon_portal_color\.png')})
    
    if online_icon:
        # This is an online activity
        try:
            # Get the platform information (e.g., "Facebook / Zoom")
            platform_spans = online_icon.find_parent('div').find('div', class_='highlight-data-text').find_all('span')
            activity_city = clean_text(platform_spans[0].text) if platform_spans else "Online"
            activity_country = "Online"
        except (AttributeError, TypeError, IndexError):
            activity_city = "Online"
            activity_country = "Online"
    else:
        # Physical activity - use original extraction logic
        try:
            location_div = soup.find('div', class_='ct-physical-activity__field-ct-act-location')
            spans = location_div.find_all('span')
            activity_city = clean_text(spans[0].text) if spans and len(spans) > 0 else "Location unknown"
            activity_country = clean_text(spans[1].text) if spans and len(spans) > 1 else "Country unknown"
        except (AttributeError, TypeError, IndexError):
            activity_city = "Location unknown"
            activity_country = "Country unknown"
    
    # Ensure values aren't empty        
    activity_city = ensure_value(activity_city, "Location unknown", "activity_city")
    activity_country = ensure_value(activity_country, "Country unknown", "activity_country")
            
    return activity_city, activity_country

def extract_activity_goal(soup: BeautifulSoup) -> str:
    """Extract activity goal handling both physical and online activities"""
    try:
        # Try physical activity goal first
        goal_div = soup.find('div', class_='ct-physical-activity__field-ct-act-goal-activity')
        
        # If not found, try online activity goal
        if not goal_div:
            goal_div = soup.find('div', class_='ct-online-activity__field-ct-act-goal-activity')
            
        # Extract goal text from the first paragraph
        if goal_div and goal_div.find('p'):
            goal_text = clean_html_text(goal_div.find('p').text)
            return ensure_value(goal_text, "No goal specified", "activity_goal")
        elif goal_div and goal_div.find('div', class_='field__item'):
            goal_text = clean_html_text(goal_div.find('div', class_='field__item').text)
            return ensure_value(goal_text, "No goal specified", "activity_goal")
    except (AttributeError, TypeError):
        pass
        
    return "No goal specified"

def extract_activity_title(soup: BeautifulSoup) -> str:
    """Extract activity title with proper HTML cleaning"""
    try:
        # Look for the title in the h1 tag
        title_tag = soup.find('h1', class_='page-title')
        if title_tag:
            title_text = clean_html_text(title_tag.text)
            return ensure_value(title_text, "Untitled Activity", "activity_title")
    except (AttributeError, TypeError):
        pass
        
    return "Untitled Activity"

def extract_activity_description(soup: BeautifulSoup) -> str:
    """Extract activity description handling both physical and online activities"""
    try:
        # Try physical activity description first
        desc_div = soup.find('div', class_='ct-physical-activity__field-ct-act-description')
        
        # If not found, try online activity description
        if not desc_div:
            desc_div = soup.find('div', class_='ct-online-activity__field-ct-act-description')
            
            # If still not found, try the general activity description class
        if not desc_div:
            desc_div = soup.find('div', class_='activity__field-ct-act-description')
            
        # Extract description text from paragraphs
        if desc_div and desc_div.find_all('p'):
            paragraphs = [clean_html_text(p.text) for p in desc_div.find_all('p')]
            clean_paragraphs = [p for p in paragraphs if p]
            if clean_paragraphs:
                return ' '.join(clean_paragraphs)
        elif desc_div and desc_div.find('div', class_='field__item'):
            desc_text = clean_html_text(desc_div.find('div', class_='field__item').text)
            if desc_text:
                return desc_text
    except (AttributeError, TypeError):
        pass
        
    return "No description available"

def extract_participants_count(soup: BeautifulSoup) -> int:
    """Extract the number of participants from the activity page"""
    try:
        # Try to find the participants count in the statistics section
        participants_div = soup.find('div', string=re.compile(r'participants', re.IGNORECASE))
        if participants_div and participants_div.find_next('div'):
            count_text = participants_div.find_next('div').text.strip()
            return ensure_integer(count_text)
    except (AttributeError, TypeError):
        pass
    
    # Default to 0 if not found
    return 0
