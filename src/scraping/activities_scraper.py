import re
import time
import random
from typing import List, Dict, Optional, Any
from bs4 import BeautifulSoup
from src.scraping.utils.request_handler import RequestHandler
from .utils.extraction_utils import (
    extract_activity_date, extract_location, 
    extract_activity_goal, extract_activity_description
)

class ActivitiesScraper:
    """
    Scraper for ESN organization activities from activities.esn.org
    """
    
    def __init__(self, retry_attempts: int = 3, retry_delay: int = 2):
        """
        Initialize the scraper with configurable retry settings
        
        Args:
            retry_attempts: Number of retry attempts for failed requests
            retry_delay: Base delay between retries (in seconds)
        """
        self.request_handler = RequestHandler(
            base_url='https://activities.esn.org',
            retry_attempts=retry_attempts,
            retry_delay=retry_delay
        )

    def get_events_page(self, organisation_id: str, page: int) -> List[Dict[str, str]]:
        """
        Get events from a specific page of an organization's activities
        
        Args:
            organisation_id: ESN organization identifier 
            page: Page number to scrape
            
        Returns:
            List of event dictionaries with title and link
        """
        params = {'page': str(page)}
        url = f'/organisation/{organisation_id}/activities'

        html = self.request_handler.make_request(url, params)
        if not html:
            return []
            
        soup = BeautifulSoup(html, 'html.parser')
        activity_articles = soup.find_all('article', class_='activities-mini-preview')

        events = []
        for article in activity_articles:
            try:
                activity_title = article.find('div', class_='eg-c-card-title').find('a').text.strip()
            except (AttributeError, TypeError):
                continue
                
            try:
                activity_link = article.find('div', class_='act-header-normal').find('a')['href']
            except (AttributeError, TypeError):
                try:
                    activity_link = article.find('div', class_='post__image').find('a')['href']
                except (AttributeError, TypeError):
                    continue
        
            events.append({
                'activity_title': activity_title,
                'activity_link': activity_link,
            })

        return events

    def scrape_activity(self, activity_id: str) -> Dict[str, Any]:
        """
        Scrape detailed information about a specific activity
        
        Args:
            activity_id: Activity URL path or ID
            
        Returns:
            Dictionary with activity details
        """
        # Ensure the activity_id is a complete URL path
        if not activity_id.startswith('/activity/'):
            activity_id = f'/activity/{activity_id}'
            
        html = self.request_handler.make_request(activity_id)
        
        if not html:
            return {
                'activity_id': activity_id,
                'error': 'Failed to retrieve activity data'
            }
            
        soup = BeautifulSoup(html, 'html.parser')
        
        # Extract activity details
        # Title extraction
        try:
            activity_title = soup.find('h1', class_='page-header').text.strip()
        except (AttributeError, TypeError):
            activity_title = "Title not found"
        
        # Date extraction with multiple format handling
        activity_date = extract_activity_date(soup)
        
        # Location extraction
        activity_city, activity_country = extract_location(soup)
        
        # Participant count
        try:
            participant_count = int(soup.find('div', class_='highlight-data-text-big').text.strip())
        except (AttributeError, TypeError, ValueError):
            participant_count = 0
        
        # Activity causes
        try:
            activity_causes = ', '.join([cause.text.strip() for cause in soup.find_all('span', class_='activity-label-cause')])
        except (AttributeError, TypeError):
            activity_causes = ""
        
        # Activity type
        try:
            activity_type = soup.find('span', class_='badge-primary').text.strip()
        except (AttributeError, TypeError):
            activity_type = ""
        
        # Activity goal
        activity_goal = extract_activity_goal(soup)
        
        # Activity description
        activity_description = extract_activity_description(soup)
        
        # SDG goals
        try:
            sdg_goals = ', '.join([img.get('title', '') for img in soup.find_all('img', class_='sdg-logo-icon')])
        except (AttributeError, TypeError):
            sdg_goals = ""
        
        # Activity objectives
        try:
            activity_objectives = ', '.join([objective.text.strip() for objective in soup.find_all('span', class_='badge-primary')])
        except (AttributeError, TypeError):
            activity_objectives = ""
        
        # Activity organizer
        try:
            activity_organiser = soup.find('a', href=re.compile(r'/organisation/')).text.strip()
        except (AttributeError, TypeError):
            activity_organiser = ""
        
        return {
            'activity_id': activity_id.split('/')[-1], 
            'activity_title': activity_title,
            'activity_date': activity_date,
            'activity_city': activity_city,
            'activity_country': activity_country,
            'participant_count': participant_count,
            'activity_causes': activity_causes,
            'activity_type': activity_type,
            'activity_goal': activity_goal,
            'activity_description': activity_description,
            'sdg_goals': sdg_goals,
            'activity_objectives': activity_objectives,
            'activity_organiser': activity_organiser
        }
    
    def get_all_organisation_activities(self, organisation_id: str, max_pages: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Get all activities from an organization
        
        Args:
            organisation_id: ESN organization identifier
            max_pages: Maximum number of pages to scrape (None for all pages)
            
        Returns:
            List of activity detail dictionaries
        """
        page = 0
        all_activities = []

        while max_pages is None or page < max_pages:
            print(f'Scraping page {page}...')
            event_links = self.get_events_page(organisation_id, page)
            if not event_links:
                break

            for event in event_links:
                activity_data = self.scrape_activity(event['activity_link'])
                if activity_data:
                    # Add organization ID for database relationships
                    activity_data['organisation_id'] = organisation_id
                    all_activities.append(activity_data)
                
                # Add a small delay to avoid overloading the server
                time.sleep(random.uniform(0.5, 1.5))

            page += 1
            
        return all_activities
    
# Example usage
# scraper = ActivitiesScraper()
# activities = scraper.get_all_organisation_activities('esn-marmara', max_pages=2)
# print(activities)