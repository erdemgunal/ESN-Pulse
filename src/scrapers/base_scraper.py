"""
Base Scraper Class

Tüm scraper sınıfları için ortak fonksiyonalite sağlayan base class.
HTTP client yönetimi, hata işleme, rate limiting, retry logic vb.
"""

import asyncio
import random
import logging
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, List
from urllib.parse import urljoin

import aiohttp
from bs4 import BeautifulSoup

from ..config import settings
from ..utils.exceptions import ScrapingError, ValidationError
from ..utils.http_client import ESNHTTPClient


logger = logging.getLogger(__name__)


class BaseScraper(ABC):
    """
    Base scraper sınıfı - tüm scraper'lar bu sınıftan inherit eder.
    
    Ortak fonksiyonalite:
    - HTTP client yönetimi
    - Rate limiting
    - Retry logic  
    - Error handling
    - User-Agent rotation
    - Logging
    """
    
    def __init__(self):
        self.http_client: Optional[ESNHTTPClient] = None
        self.session_stats = {
            "requests_made": 0,
            "requests_failed": 0,
            "requests_successful": 0,
            "retries_performed": 0
        }
        
    async def __aenter__(self):
        """Async context manager entry."""
        await self._initialize_session()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self._cleanup_session()
        
    async def _initialize_session(self):
        """Initialize HTTP session."""
        if not self.http_client:
            self.http_client = ESNHTTPClient()
            await self.http_client.__aenter__()
        logger.info(f"Initialized {self.__class__.__name__} session")
        
    async def _cleanup_session(self):
        """Cleanup HTTP session."""
        if self.http_client:
            await self.http_client.__aexit__(None, None, None)
            self.http_client = None
        
        logger.info(
            f"{self.__class__.__name__} session ended. Stats: {self.session_stats}"
        )
    
    async def get_page_content(
        self, 
        url: str, 
        max_retries: Optional[int] = None
    ) -> str:
        """
        Get page content with error handling and retries.
        
        Args:
            url: URL to fetch
            max_retries: Override default retry count
            
        Returns:
            HTML content as string
            
        Raises:
            ScrapingError: If all retries failed
        """
        if not self.http_client:
            await self._initialize_session()
            
        max_retries = max_retries or settings.MAX_RETRIES
        
        for attempt in range(max_retries + 1):
            try:
                self.session_stats["requests_made"] += 1
                
                # Rate limiting
                delay = settings.SCRAPING_DELAY
                await asyncio.sleep(delay)
                
                print(f"============================== 📡 Sending request to: {url} ==============================")
                content = await self.http_client.get_with_retry(url, max_retries=1)
                self.session_stats["requests_successful"] += 1
                
                logger.debug(f"Successfully fetched: {url}")
                return content
                
            except Exception as e:
                self.session_stats["requests_failed"] += 1
                
                if attempt < max_retries:
                    # Exponential backoff
                    wait_time = 2 ** attempt
                    logger.warning(
                        f"Request failed (attempt {attempt + 1}/{max_retries + 1}). "
                        f"Retrying in {wait_time}s. URL: {url}, Error: {str(e)}"
                    )
                    await asyncio.sleep(wait_time)
                    self.session_stats["retries_performed"] += 1
                else:
                    logger.error(f"All retries failed for URL: {url}")
                    raise ScrapingError(url, 0, str(e))
    
    async def parse_html(self, content: str, url: str) -> BeautifulSoup:
        """
        Parse HTML content using BeautifulSoup.
        
        Args:
            content: HTML content
            url: Source URL (for error context)
            
        Returns:
            BeautifulSoup object
            
        Raises:
            ScrapingError: If parsing fails
        """
        try:
            soup = BeautifulSoup(content, 'html.parser')
            
            # Basic validation
            if not soup.find('html'):
                raise ValueError("Invalid HTML content")
                
            return soup
            
        except Exception as e:
            logger.error(f"HTML parsing failed for {url}: {str(e)}")
            raise ScrapingError(url, 0, f"HTML parsing failed: {str(e)}")
    
    async def validate_slug_url(self, slug: str, base_url: str) -> bool:
        """
        Validate if a slug exists by making HEAD request.
        
        Args:
            slug: Platform slug to validate
            base_url: Base URL template
            
        Returns:
            True if URL exists (200 OK), False otherwise
        """
        if not self.http_client:
            raise RuntimeError("HTTP client not initialized")
            
        url = base_url.format(slug=slug)
        try:
            response = await self.http_client.head(url)
            exists = response.status == 200
            logger.debug(f"Slug validation for {slug}: {exists}")
            return exists
            
        except Exception as e:
            logger.warning(f"Slug validation failed for {slug}: {str(e)}")
            return False
    
    def log_stats(self):
        """Log current session statistics."""
        logger.info(f"{self.__class__.__name__} Statistics: {self.session_stats}")
        
    @abstractmethod
    async def scrape(self, *args, **kwargs) -> Dict[str, Any]:
        """
        Main scraping method - must be implemented by subclasses.
        
        Returns:
            Dictionary containing scraped data and metadata
        """
        pass
    
    @abstractmethod
    async def validate_data(self, data: Dict[str, Any]) -> bool:
        """
        Validate scraped data - must be implemented by subclasses.
        
        Args:
            data: Scraped data to validate
            
        Returns:
            True if data is valid, False otherwise
        """
        pass 