"""
ActivitiesAndStatisticsScraper - activities.esn.org platformundan veri toplama modülü

Bu modül:
- Şube etkinliklerini paginasyon ile çeker
- Etkinlik detaylarını tek tek çeker
- İstatistik verilerini JSON API'den çeker
- activities, statistics ve relationship tablolarına veri yazar

Workflow:
1. can_scrape_activities=True olan şubeleri al
2. Her şube için pagination bilgisini çek
3. Sayfa gruplarını paralel olarak işle
4. Her etkinlik için detay sayfasını çek
5. İstatistik JSON'unu çek ve parse et
6. Veritabanına UPSERT et
"""

import asyncio
import json
import logging
from typing import Dict, List, Any, Optional, Tuple
from urllib.parse import urljoin
from datetime import datetime, date

from ..models.activity import ActivityModel
from ..models.section_statistics import SectionStatisticsModel
from ..database.operations import DatabaseOperations
from ..utils.date_parser import parse_event_date_range
from .base_scraper import BaseScraper

logger = logging.getLogger(__name__)


class ActivitiesAndStatisticsScraper(BaseScraper):
    """
    activities.esn.org platformundan etkinlik ve istatistik verilerini çeken scraper.
    """
    
    def __init__(self):
        super().__init__()
        self.base_url = "https://activities.esn.org"
        self.db_ops: Optional[DatabaseOperations] = None
        
        # CSS selectors for activity parsing
        self.activity_selectors = {
            'container': 'article.ct-physical-activity.activities-mini-preview, article.ct-online-activity.activities-mini-preview',
            'title': '.field__item h1, .activity-label',
            'event_slug': '.url',
            'description': '.ct-physical-activity__field-ct-act-description .field__item',
            'dates': '.highlight-dates-single span',
            'location': '.highlight-data-text span',
            'organisers': '.pseudo__organisers .pseudo__organiser a',
            'participants': '.highlight-data-number .highlight-data-text-big',
            'sdgs': '.field-sdgs-wrapper img',
            'objectives': '.activity__objectives .field__item span',
            'causes': '.activity-causes .activity-label a',
            'activity_type': '.activity-types .activity-type a',
            'pagination_last': '.pager__item--last a'
        }
    
    async def __aenter__(self):
        await super().__aenter__()
        self.db_ops = DatabaseOperations()
        await self.db_ops.__aenter__()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.db_ops:
            await self.db_ops.__aexit__(exc_type, exc_val, exc_tb)
        await super().__aexit__(exc_type, exc_val, exc_tb)
    
    async def scrape(
        self, 
        section_slug: Optional[str] = None,
        max_sections: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Ana scraping metodu - etkinlik ve istatistik verilerini çeker.
        
        Args:
            section_slug: Belirli bir şube için scraping (optional)
            max_sections: İşlenecek maksimum şube sayısı (optional)
        
        Returns:
            Dict containing scraping results and statistics
        """
        async with self as scraper:
            logger.info("Starting ActivitiesAndStatisticsScraper...")
            
            results = {
                "sections_processed": 0,
                "activities_processed": 0,
                "statistics_processed": 0,
                "errors": [],
                "start_time": datetime.now(),
                "end_time": None
            }
            
            try:
                # Get sections to process
                if section_slug:
                    sections = [await self.db_ops.get_section_by_slug(section_slug)]
                    if not sections[0]:
                        raise ValueError(f"Section not found: {section_slug}")
                else:
                    sections = await self.db_ops.get_sections_to_scrape(
                        limit=max_sections
                    )
                
                logger.info(f"Processing {len(sections)} sections")
                
                # Process each section
                for section in sections:
                    try:
                        if section['activities_platform_slug'] == 'esn-lille':
                            section_results = await self.process_section(section)
                            
                            # results["sections_processed"] += 1
                            # results["activities_processed"] += section_results.get("activities_count", 0)
                            # results["statistics_processed"] += section_results.get("statistics_count", 0)
                            
                            # logger.info(f"Processed section {section['name']}: "
                            #         f"{section_results.get('activities_count', 0)} activities, "
                            #         f"{section_results.get('statistics_count', 0)} statistics")
                        
                    except Exception as e:
                        error_msg = f"Failed to process section {section['name']}: {str(e)}"
                        logger.error(error_msg)
                        results["errors"].append(error_msg)
                
            #     results["end_time"] = datetime.now()
            #     duration = (results["end_time"] - results["start_time"]).total_seconds()
                
            #     logger.info(f"ActivitiesAndStatisticsScraper completed in {duration:.1f}s. "
            #                f"Processed {results['sections_processed']} sections, "
            #                f"{results['activities_processed']} activities")
                
            except Exception as e:
                logger.error(f"ActivitiesAndStatisticsScraper failed: {str(e)}")
                results["errors"].append(str(e))
                raise
                
            # return results
    
    async def process_section(self, section) -> Dict[str, Any]:
        """
        Process a single section - extract activities and statistics.
        
        Args:
            section: Section database record
            
        Returns:
            Dict with processing results
        """
        activities_count = 0
        statistics_count = 0
        
        # 1. Process activities
        try:
            activities = await self.extract_section_activities(section['activities_platform_slug'])
            
            # for activity in activities:
            #     await self.db_ops.upsert_activity(activity, section['id'])
            #     activities_count += 1
                
        except Exception as e:
            logger.error(f"Failed to process activities for {section['name']}: {str(e)}")
        
        # 2. Process statistics
        # try:
        #     statistics = await self.extract_section_statistics(section['activities_platform_slug'])
        #     if statistics:
        #         await self.db_ops.upsert_section_statistics(statistics, section['id'])
        #         statistics_count = 1
                
        # except Exception as e:
        #     logger.error(f"Failed to process statistics for {section['name']}: {str(e)}")
        
        # # 3. Update last_scraped timestamp
        # await self.db_ops.update_section_last_scraped(section['id'])
        
        # return {
        #     "activities_count": activities_count,
        #     "statistics_count": statistics_count
        # }
    
    async def extract_section_activities(self, activities_slug: str) -> List[ActivityModel]:
        """
        Extract all activities for a section with pagination handling.
        
        Args:
            activities_slug: Section slug on activities platform
            
        Returns:
            List of ActivityModel objects
        """
        base_url = f"{self.base_url}/organisation/{activities_slug}/activities"
        print(f"🎯 Fetching activities from: {base_url}")
        
        # 1. Get pagination info
        total_pages = await self.get_total_pages(base_url)
        logger.debug(f"Section {activities_slug} has {total_pages} pages")
        
        if total_pages == 0:
            return []
        
        # 2. Process pages in chunks
        from ..config import settings
        chunk_size = settings.PAGINATION_CHUNK_SIZE
        page_chunks = [
            list(range(i, min(i + chunk_size, total_pages)))
            for i in range(0, total_pages, chunk_size)
        ]
        
        all_activities = []
        
        # Process chunks sequentially to avoid overwhelming the server
        for chunk in page_chunks:
            chunk_activities = await self.process_activity_pages_chunk(
                activities_slug, chunk
            )
            all_activities.extend(chunk_activities)
            
            # Small delay between chunks
            await asyncio.sleep(1.0)
        
        logger.info(f"Extracted {len(all_activities)} activities for {activities_slug}")
        # return all_activities
    
    async def get_total_pages(self, base_url: str) -> int:
        """
        Get total number of pages from pagination navigation.
        
        Args:
            base_url: Base activities URL
            
        Returns:
            Total number of pages (0-indexed)
        """
        try:
            url = f"{base_url}?page=0"
            content = await self.get_page_content(url)
            soup = await self.parse_html(content, url)
            
            # Find "Last" link in pagination
            last_link = soup.select_one(self.activity_selectors['pagination_last'])
            
            if not last_link:
                return 1  # Only one page
            
            href = last_link.get('href', '')
            if 'page=' in href:
                try:
                    last_page = int(href.split('page=')[-1].split('&')[0])
                    return last_page + 1  # Convert to count (0-indexed to 1-indexed)
                except ValueError:
                    pass
            
            return 1
            
        except Exception as e:
            logger.warning(f"Failed to get pagination info for {base_url}: {str(e)}")
            return 1
    
    async def process_activity_pages_chunk(
        self, 
        activities_slug: str, 
        page_numbers: List[int]
    ) -> List[ActivityModel]:
        """
        Process a chunk of activity pages in parallel.
        
        Args:
            activities_slug: Section slug
            page_numbers: List of page numbers to process
            
        Returns:
            List of ActivityModel objects
        """
        tasks = []
        
        for page_num in page_numbers:
            url = f"{self.base_url}/organisation/{activities_slug}/activities?page={page_num}"
            tasks.append(self.extract_activities_from_page(url))
        
        # Execute tasks in parallel
        page_results = await asyncio.gather(*tasks, return_exceptions=True)
        
        all_activities = []
        for i, result in enumerate(page_results):
            if isinstance(result, Exception):
                logger.error(f"Failed to process page {page_numbers[i]}: {str(result)}")
                continue
            
            all_activities.extend(result)
        
        return all_activities
    
    async def extract_activities_from_page(self, url: str) -> List[ActivityModel]:
        """
        Extract activities from a single page.
        
        Args:
            url: Page URL
            
        Returns:
            List of ActivityModel objects
        """
        activities = []
        
        try:
            content = await self.get_page_content(url)
            soup = await self.parse_html(content, url)
            
            # Find all activity containers
            activity_containers = soup.select(self.activity_selectors['container'])
            
            for container in activity_containers:
                try:
                    activity = await self.parse_activity_container(container)
                    if activity:
                        activities.append(activity)
                        
                except Exception as e:
                    logger.warning(f"Failed to parse activity container: {str(e)}")
                    continue
            
        except Exception as e:
            logger.error(f"Failed to extract activities from page {url}: {str(e)}")
        
        return activities
    
    async def parse_activity_container(self, container) -> Optional[ActivityModel]:
        """
        Parse a single activity container element.
        
        Args:
            container: BeautifulSoup element containing activity data
            
        Returns:
            ActivityModel object or None if parsing fails
        """
        try:
            # Extract basic fields
            title_elem = container.select_one(self.activity_selectors['title'])
            print(title_elem)
            title = title_elem.get_text(strip=True) if title_elem else ""
            
            url_elem = container.select_one(self.activity_selectors['event_slug'])
            url = url_elem.get('href', '') if url_elem else ""
            event_slug = url.split('/')[-1] if url else ""
            
            desc_elem = container.select_one(self.activity_selectors['description'])
            description = desc_elem.get_text(strip=True) if desc_elem else ""
            
            # Extract dates
            dates_elem = container.select_one(self.activity_selectors['dates'])
            start_date, end_date = parse_event_date_range(dates_elem.get_text(strip=True)) if dates_elem else (None, None)
            
            # Extract location
            location_elem = container.select_one(self.activity_selectors['location'])
            city, country_code = self.parse_location(location_elem.get_text(strip=True)) if location_elem else (None, None)
            
            # Extract participants
            participants_elem = container.select_one(self.activity_selectors['participants'])
            participants = self.parse_participants(participants_elem.get_text(strip=True)) if participants_elem else 0
            
            # Extract type
            type_elem = container.select_one(self.activity_selectors['activity_type'])
            activity_type = type_elem.get_text(strip=True) if type_elem else ""
            
            # Extract lists
            organisers = self.extract_text_list(container, self.activity_selectors['organisers'])
            sdgs = self.extract_text_list(container, self.activity_selectors['sdgs'], attr='alt')
            objectives = self.extract_text_list(container, self.activity_selectors['objectives'])
            causes = self.extract_text_list(container, self.activity_selectors['causes'])
            
            # Validate required fields
            if not all([title, event_slug, description, start_date]):
                logger.warning(f"Missing required fields for activity: {title}")
                return None
            
            # Calculate is_future_event
            is_future_event = start_date > date.today() if start_date else False
            
            # activity = ActivityModel(
            #     event_slug=event_slug,
            #     url=urljoin(self.base_url, url) if url else "",
            #     title=title,
            #     description=description,
            #     start_date=start_date,
            #     end_date=end_date,
            #     city=city,
            #     country_code=country_code,
            #     participants=participants,
            #     activity_type=activity_type,
            #     is_future_event=is_future_event,
            #     organisers=organisers,
            #     causes=causes,
            #     sdgs=sdgs,
            #     objectives=objectives,
            #     is_valid=True
            # )
            
            return activity
            
        except Exception as e:
            logger.error(f"Failed to parse activity container: {str(e)}")
            return None
    
    def parse_location(self, location_text: str) -> Tuple[Optional[str], Optional[str]]:
        """Parse location text to extract city and country code."""
        if not location_text:
            return None, None
        
        # Location format is usually "City, Country" or just "City"
        parts = [part.strip() for part in location_text.split(',')]
        
        if len(parts) >= 2:
            city = parts[0]
            country = parts[-1]
            
            # Try to convert country name to code
            country_code = self.country_name_to_code(country)
            return city, country_code
        elif len(parts) == 1:
            return parts[0], None
        
        return None, None
    
    def parse_participants(self, participants_text: str) -> int:
        """Parse participants text to extract number."""
        if not participants_text:
            return 0
        
        try:
            # Extract number from text
            import re
            numbers = re.findall(r'\d+', participants_text)
            return int(numbers[0]) if numbers else 0
        except (ValueError, IndexError):
            return 0
    
    def extract_text_list(
        self, 
        container, 
        selector: str, 
        attr: Optional[str] = None
    ) -> List[str]:
        """Extract list of text values from container using selector."""
        elements = container.select(selector)
        texts = []
        
        for elem in elements:
            if attr:
                text = elem.get(attr, '').strip()
            else:
                text = elem.get_text(strip=True)
            
            if text:
                texts.append(text)
        
        return texts
    
    def country_name_to_code(self, country_name: str) -> Optional[str]:
        """Convert country name to 2-letter code."""
        # Simple mapping - in production, use a proper country mapping library
        country_mapping = {
            'Turkey': 'TR',
            'Germany': 'DE', 
            'France': 'FR',
            'Italy': 'IT',
            'Spain': 'ES',
            'Poland': 'PL',
            # Add more mappings as needed
        }
        
        return country_mapping.get(country_name)
    
    async def extract_section_statistics(self, activities_slug: str) -> Optional[SectionStatisticsModel]:
        """
        Extract statistics for a section from JSON API.
        
        Args:
            activities_slug: Section slug on activities platform
            
        Returns:
            SectionStatisticsModel object or None
        """
        url = f"{self.base_url}/organisation/{activities_slug}/statistics"
        print(f"📊 Fetching statistics from: {url}")
        
        try:
            content = await self.get_page_content(url)
            
            # Parse JSON response
            stats_data = json.loads(content)
            activities_stats = stats_data.get('activities_statistics', {})
            
            # Extract overall statistics
            total_activities = activities_stats.get('total_activities', {}).get('values', [])
            physical_activities = total_activities[0][1] if len(total_activities) > 0 else 0
            online_activities = total_activities[1][1] if len(total_activities) > 1 else 0
            
            total_participants = activities_stats.get('total_participants', {}).get('values', [])
            total_local_students = total_participants[0][1] if len(total_participants) > 0 else 0
            total_international_students = total_participants[1][1] if len(total_participants) > 1 else 0
            total_coordinators = total_participants[2][1] if len(total_participants) > 2 else 0
            
            # Extract detailed statistics
            cause_statistics = self.parse_detailed_statistics(activities_stats, 'causes')
            type_statistics = self.parse_detailed_statistics(activities_stats, 'types')
            participant_statistics = self.parse_detailed_statistics(activities_stats, 'participants')
            
            statistics = SectionStatisticsModel(
                section_id=0,  # Will be set when saving
                physical_activities=physical_activities,
                online_activities=online_activities,
                total_local_students=total_local_students,
                total_international_students=total_international_students,
                total_coordinators=total_coordinators,
                cause_statistics=cause_statistics,
                type_statistics=type_statistics,
                participant_statistics=participant_statistics
            )
            
            return statistics
            
        except Exception as e:
            logger.error(f"Failed to extract statistics for {activities_slug}: {str(e)}")
            return None
    
    def parse_detailed_statistics(self, activities_stats: Dict, category: str) -> Dict[str, Dict[str, int]]:
        """Parse detailed statistics for causes, types, or participants."""
        result = {}
        
        for stat_type in ['total', 'physical', 'online']:
            key = f"{stat_type}_{category}"
            values = activities_stats.get(key, {}).get('values', [])
            
            for item in values:
                if len(item) >= 2:
                    name = item[0]
                    count = item[1]
                    
                    if name not in result:
                        result[name] = {}
                    
                    result[name][stat_type] = count
        
        return result
    
    async def validate_data(self, data: Dict[str, Any]) -> bool:
        """
        Validate scraped data quality.
        
        Args:
            data: Scraped data dictionary
            
        Returns:
            True if data meets quality criteria
        """
        try:
            sections_processed = data.get("sections_processed", 0)
            activities_processed = data.get("activities_processed", 0)
            error_count = len(data.get("errors", []))
            
            # Check if any sections were processed
            if sections_processed == 0:
                logger.warning("No sections processed")
                return False
            
            # Check average activities per section
            if sections_processed > 0:
                avg_activities = activities_processed / sections_processed
                if avg_activities < 5:  # Expect at least 5 activities per section on average
                    logger.warning(f"Low activity count: {avg_activities:.1f} per section")
                    return False
            
            # Check error rate
            if error_count > sections_processed * 0.2:  # Max 20% error rate
                logger.warning(f"High error rate: {error_count}/{sections_processed}")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Data validation failed: {str(e)}")
            return False 