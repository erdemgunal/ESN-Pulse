import json
from typing import Dict, Any
from bs4 import BeautifulSoup
from .utils.request_handler import RequestHandler
from .utils.extraction_utils import extract_statistic, extract_causes, extract_types

class StatisticsScraper:
    """
    Scraper for ESN organization statistics from activities.esn.org
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
        
    def scrape_statistics(self, organisation_id: str) -> Dict[str, Any]:
        """
        Scrape statistics for a specific ESN organization
        
        Args:
            organisation_id: ESN organization identifier
            
        Returns:
            Dictionary with statistics data, structured as on the website
        """
        url = f'/organisation/{organisation_id}/statistics'
        html = self.request_handler.make_request(url)
        
        if not html:
            return {
                'organisation_id': organisation_id,
                'error': 'Failed to retrieve statistics data'
            }
            
        soup = BeautifulSoup(html, 'html.parser')
        
        # Extract JSON data from the script tag
        script_tag = soup.find('script', {'data-drupal-selector': 'drupal-settings-json'})
        
        if not script_tag:
            return {
                'organisation_id': organisation_id,
                'error': 'No JSON data found'
            }
            
        try:
            json_data = json.loads(script_tag.string)
            statistics = json_data.get('activities_statistics', {})
        except json.JSONDecodeError:
            return {
                'organisation_id': organisation_id,
                'error': 'Failed to parse JSON data'
            }
            
        # Format the result to match the website structure
        result = {
            'organisation_id': organisation_id,
            'general_statistics': {
                'total_activities': extract_statistic(statistics, 'total_activities'),
                'total_participants': extract_statistic(statistics, 'total_participants'),
                'total_activities_by_cause': extract_causes(statistics, 'total_causes')
            },
            'physical_activities_statistics': {
                'total_participants': extract_statistic(statistics, 'physical_participants'),
                'total_activities_by_cause': extract_causes(statistics, 'physical_causes'),
                'total_activities_by_type': extract_types(statistics, 'physical_types')
            },
            'online_activities_statistics': {
                'total_participants': extract_statistic(statistics, 'online_participants'),
                'total_activities_by_cause': extract_causes(statistics, 'online_causes'),
                'total_activities_by_type': extract_types(statistics, 'online_types')
            }
        }
        
        return result