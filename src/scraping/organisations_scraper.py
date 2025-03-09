from typing import Dict, Optional, Any
from bs4 import BeautifulSoup
from src.scraping.utils.request_handler import RequestHandler
from src.scraping.utils.extraction_utils import extract_statistics, ensure_integer

class OrganisationsScraper:
    """
    Scraper for ESN organization details from activities.esn.org
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

    def scrape_organisation_details(self, organisation_id: str) -> Dict[str, Any]:
        """
        Scrape detailed information about a specific ESN organization
        
        Args:
            organisation_id: ESN organization identifier
            
        Returns:
            Dictionary with organization details
        """
        url = f'/organisation/{organisation_id}'
        html = self.request_handler.make_request(url)
        
        if not html:
            return {
                'organisation_id': organisation_id,
                'error': 'Failed to retrieve organization data'
            }
            
        soup = BeautifulSoup(html, 'html.parser')
        
        # Extract organization name
        try:
            organisation_name = soup.find('header').find('h1', class_='page-header').text.strip()
        except (AttributeError, TypeError):
            organisation_name = "Name not found"
        
        # Extract statistics
        statistics = extract_statistics(soup)
        
        # Convert statistics values from strings to integers
        for key, value in statistics.items():
            if isinstance(value, str) and value.strip().isdigit():
                statistics[key] = ensure_integer(value)
        
        return {
            'organisation_id': organisation_id,
            'organisation_name': organisation_name,
            'statistics': statistics
        }