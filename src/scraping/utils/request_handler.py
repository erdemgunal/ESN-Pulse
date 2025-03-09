import requests
import time
import random
from typing import Dict, Optional
from fake_useragent import UserAgent

class RequestHandler:
    """
    Handler for making HTTP requests with retry logic and configurable settings
    """
    
    def __init__(
        self, 
        base_url: str = None,
        retry_attempts: int = 3, 
        retry_delay: int = 2,
        headers: Optional[Dict[str, str]] = None
    ):
        """
        Initialize the request handler with configurable settings
        
        Args:
            base_url: Base URL for requests
            retry_attempts: Number of retry attempts for failed requests
            retry_delay: Base delay between retries (in seconds)
            headers: Custom headers to use for requests
        """
        self.base_url = base_url
        self.retry_attempts = retry_attempts
        self.retry_delay = retry_delay
        self.session = requests.Session()
        
        # Set default headers if none provided
        if headers is None:
            self.headers = {
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Sec-Fetch-Site': 'none',
                'Sec-Fetch-Mode': 'navigate',
                'User-Agent': UserAgent().chrome,
                'Accept-Language': 'en-US,en;q=0.9',
                'Sec-Fetch-Dest': 'document',
                'Priority': 'u=0, i',
            }
        else:
            self.headers = headers

    def make_request(self, url: str, params: Optional[Dict[str, str]] = None) -> Optional[str]:
        """
        Make an HTTP request with retry logic
        
        Args:
            url: URL to request
            params: Optional query parameters
            
        Returns:
            Response text if successful, None otherwise
        """
        # Prepend base_url if url doesn't start with http and base_url is set
        if self.base_url and not url.startswith(('http://', 'https://')):
            full_url = f"{self.base_url.rstrip('/')}/{url.lstrip('/')}"
        else:
            full_url = url
            
        for attempt in range(self.retry_attempts):
            try:
                response = self.session.get(
                    full_url,
                    params=params,
                    headers=self.headers,
                    timeout=10
                )
                response.raise_for_status()
                return response.text
            except (requests.RequestException, requests.HTTPError) as e:
                if attempt == self.retry_attempts - 1:
                    return None
                    
                # Exponential backoff with jitter
                delay = self.retry_delay * (2 ** attempt) + random.uniform(0, 1)
                time.sleep(delay)
                
                # Rotate user agent on retry
                self.headers['User-Agent'] = UserAgent().chrome
        
        return None