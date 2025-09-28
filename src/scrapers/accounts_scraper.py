import logging
from typing import Dict, Any, Optional
from datetime import datetime
import json

from ..database.operations import DatabaseOperations
from .base_scraper import BaseScraper
from .extractors.country_extractor import extract_countries
from .extractors.section_extractor import extract_sections_for_country
from .validators.account_validator import validate_activities_slug, validate_scraping_data

logger = logging.getLogger(__name__)

class AccountsScraper(BaseScraper):
    def __init__(self):
        super().__init__()
        self.base_url = "https://accounts.esn.org"
        self.db_ops: Optional[DatabaseOperations] = None
    
    async def __aenter__(self):
        await super().__aenter__()
        self.db_ops = DatabaseOperations()
        await self.db_ops.__aenter__()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.db_ops:
            await self.db_ops.__aexit__(exc_type, exc_val, exc_tb)
        await super().__aexit__(exc_type, exc_val, exc_tb)
    
    async def scrape(self) -> Dict[str, Any]:
        async with self as scraper:
            logger.info("Starting AccountsScraper...")
            results = {
                "countries_processed": 0,
                "sections_processed": 0,
                "sections_validated": 0,
                "errors": [],
                "start_time": datetime.now(),
                "end_time": None
            }
            
            try:
                # Initialize HTTP client
                await self._initialize_session()
                
                # 1. Extract countries
                countries = await extract_countries(self, self.base_url)
                logger.info(f"Found {len(countries)} countries")
                
                # 2. Save countries to database
                for country in countries:
                    country_data = country.dict()
                    # Convert HttpUrl to string for database storage
                    if 'url' in country_data:
                        country_data['url'] = str(country_data['url'])
                    await self.db_ops.insert_country(country_data)
                results["countries_processed"] = len(countries)
                
                # 3. Extract sections for each country, prioritizing by last_scraped
                total_sections = 0
                validated_sections = 0
                
                for country in countries:
                    try:
                        # if country.country_code == 'TR':
                        sections = await extract_sections_for_country(
                            self,
                            country.country_code,
                            self.base_url
                        )
                        logger.info(f"Found {len(sections)} sections for {country.name}")

                        # Update country's section count
                        await self.db_ops.update_country_section_count(country.country_code, len(sections))

                        # Validate and save sections
                        for section in sections:
                            # Generate and validate activities slug
                            if await validate_activities_slug(self, section):
                                validated_sections += 1

                            section_data = section.dict()
                            
                            # Convert all special types to appropriate database format
                            if section_data.get('website'):
                                section_data['website'] = str(section_data['website'])
                            
                            if section_data.get('latitude'):
                                section_data['latitude'] = float(section_data['latitude'])
                            
                            if section_data.get('longitude'):
                                section_data['longitude'] = float(section_data['longitude'])
                            
                            # Convert URL fields to strings
                            url_fields = [field for field in section_data.keys() if field.endswith('_url')]
                            for field in url_fields:
                                if field in section_data and section_data[field] is not None:
                                    section_data[field] = str(section_data[field])
                            
                            # Convert social_media to JSON string
                            if section_data.get('social_media'):
                                section_data['social_media'] = json.dumps(dict(section_data['social_media']))
                            
                            inserted_section = await self.db_ops.insert_section(section_data)
                            
                            # Update last_scraped for the section
                            if inserted_section:
                                await self.db_ops.update_section_last_scraped(inserted_section['id'])
                            
                            total_sections += 1
                            
                    except Exception as e:
                        error_msg = f"Failed to process country {country.country_code}: {str(e)}"
                        logger.error(error_msg)
                        results["errors"].append(error_msg)
                
                results["sections_processed"] = total_sections
                results["sections_validated"] = validated_sections
                
                results["end_time"] = datetime.now()
                duration = (results["end_time"] - results["start_time"]).total_seconds()
                
                logger.info(f"AccountsScraper completed in {duration:.1f}s. "
                          f"Processed {total_sections} sections, "
                          f"validated {validated_sections} activities slugs")
                
                # Validate results
                if not await self.validate_data(results):
                    logger.warning("Data validation failed")
                
            except Exception as e:
                logger.error(f"AccountsScraper failed: {str(e)}")
                results["errors"].append(str(e))
                raise
                
            return results

    async def validate_data(self, data: Dict[str, Any]) -> bool:
        return await validate_scraping_data(data)