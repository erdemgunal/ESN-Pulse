"""
AccountsScraper - accounts.esn.org platformundan veri toplama modülü

Bu modül:
- Tüm ülkeleri ve şubeleri çeker
- Şube bilgilerini ve detaylarını toplar  
- activities_platform_slug doğrulaması yapar
- sections ve countries tablolarına veri yazar

Workflow:
1. /countries sayfasından ülke listesi çek
2. Her ülke için /country/<code> sayfasından şube listesi çek
3. Her şube için slug oluştur ve doğrula
4. Veritabanına UPSERT et
"""

import json
import logging
from typing import Dict, List, Any, Optional
from urllib.parse import urljoin
from ..models.country import CountryModel
from ..models.section import SectionModel 
from ..database.operations import DatabaseOperations
from ..utils.slug_generator import generate_activities_slug
from .base_scraper import BaseScraper

logger = logging.getLogger(__name__)


class AccountsScraper(BaseScraper):
    """
    accounts.esn.org platformundan ülke ve şube bilgilerini çeken scraper.
    """
    
    def __init__(self):
        super().__init__()
        self.base_url = "https://accounts.esn.org"
        self.db_ops: Optional[DatabaseOperations] = None
        
        # CSS selectors
        self.selectors = {
            'country_links': 'a[href*="/country/"]',
            'section_items': 'span.field-content',
            'section_links': '.views-view-grid a[href*="/section/"]',
            'contact_email': '.field--name-field-email .field--item',
            'contact_website': 'a[title="Website of the organisation"]',
            'university_name': '.field--name-field-university-name .field--item',
            'address': '.field--name-field-address .field--item .address',
            'coordinates': '.geolocation-location[data-lat]',
            'logo': '.center-block.img-responsive[alt*="Logo"]',
            'social_media': 'a[title*="profile"]',
            'city': '.field--name-field-city .field--item'
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
    
    async def scrape(self) -> Dict[str, Any]:
        """
        Ana scraping metodu - tüm ülke ve şube verilerini çeker.
        
        Returns:
            Dict containing scraping results and statistics
        """
        async with self as scraper:
            logger.info("Starting AccountsScraper...")
            results = {
                "countries_processed": 0,
                "sections_processed": 0,
                "sections_validated": 0,
                "errors": [],
                "start_time": None,
                "end_time": None
            }
            
            try:
                # Initialize HTTP client
                await self._initialize_session()
                
                # 1. Extract countries
                countries = await self.extract_countries()
                logger.info(f"Found {len(countries)} countries")
                
                # 2. Save countries to database
                for country in countries:
                    country_data = country.dict()
                    # Convert HttpUrl to string for database storage
                    if 'url' in country_data:
                        country_data['url'] = str(country_data['url'])
                    await self.db_ops.insert_country(country_data)
                results["countries_processed"] = len(countries)
                
                # 3. Get sections ordered by last_scraped
                existing_sections = await self.db_ops.get_sections_by_last_scraped()
                existing_sections_dict = {section['accounts_platform_slug']: section for section in existing_sections}
                
                # 4. Extract sections for each country, prioritizing by last_scraped
                total_sections = 0
                validated_sections = 0
                
                for country in countries:
                    try:
                        sections = await self.extract_sections_for_country(country.country_code)
                        logger.info(f"Found {len(sections)} sections for {country.name}")

                        # Validate and save sections
                        for section in sections:
                            # Generate and validate activities slug
                            if await self.validate_activities_slug(section):
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
                            
                            print("Section data to be inserted:", section_data)
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
                
                logger.info(f"AccountsScraper completed. Processed {total_sections} sections, "
                           f"validated {validated_sections} activities slugs")
                
            except Exception as e:
                logger.error(f"AccountsScraper failed: {str(e)}")
                results["errors"].append(str(e))
                raise
                
            return results
    
    async def extract_countries(self) -> List[CountryModel]:
        """
        Extract all countries from accounts.esn.org main page.
        
        Returns:
            List of CountryModel objects
        """
        url = f"{self.base_url}/"
        print(f"🌍 Fetching countries from: {url}")
        
        try:
            print(f"🔍 Initializing HTTP client for: {url}")
            await self._initialize_session()
            
            print(f"📥 Getting page content from: {url}")
            content = await self.get_page_content(url)
            print(f"📄 Content length: {len(content)} bytes")
            
            print(f"🔄 Parsing HTML from: {url}")
            soup = await self.parse_html(content, url)
            
            countries = []
            country_links = soup.select(self.selectors['country_links'])
            print(f"📋 Found {len(country_links)} country links")
            
            for link in country_links:
                # if 'fr' in link.get('href', ''):
                try:
                    href = link.get('href', '')
                    if '/country/' not in href:
                        print(f"⚠️ Skipping invalid link: {href}")
                        continue
                        
                    # Extract country code from URL
                    country_code = href.split('/country/')[-1].strip('/')
                    if not country_code or len(country_code) != 2:
                        print(f"⚠️ Invalid country code: {country_code}")
                        continue
                        
                    name = link.get_text(strip=True)
                    if not name:
                        print(f"⚠️ Empty country name for code: {country_code}")
                        continue
                    
                    country = CountryModel(
                        country_code=country_code.upper(),
                        name=name,
                        slug=country_code.lower(),
                        url=urljoin(self.base_url, href),
                        section_count=0  # Will be updated later
                    )
                    
                    countries.append(country)
                    print(f"✅ Extracted country: {country.name} ({country.country_code})")
                    logger.debug(f"Extracted country: {country.name} ({country.country_code})")
                    
                except Exception as e:
                    print(f"❌ Failed to extract country from link {link}: {str(e)}")
                    logger.warning(f"Failed to extract country from link {link}: {str(e)}")
                    continue
            
            print(f"📊 Total countries extracted: {len(countries)}")
            return countries
            
        except Exception as e:
            print(f"❌ Failed to extract countries: {str(e)}")
            logger.error(f"Failed to extract countries: {str(e)}")
            return []
    
    async def extract_sections_for_country(self, country_code: str) -> List[SectionModel]:
        """
        Extract all sections for a specific country.
        
        Args:
            country_code: Country code (e.g., 'TR', 'DE')
            
        Returns:
            List of SectionModel objects
        """
        url = f"{self.base_url}/country/{country_code.lower()}"
        print(f"🏫 Fetching sections for {country_code} from: {url}")
        content = await self.get_page_content(url)
        soup = await self.parse_html(content, url)

        sections = []
        section_links = soup.select(self.selectors['section_links'])
        
        # Remove duplicates by using a set of hrefs
        seen_hrefs = set()
        unique_links = []
        for link in section_links:
            href = link.get('href', '')
            if href not in seen_hrefs:
                seen_hrefs.add(href)
                unique_links.append(link)
        
        print(f"Found {len(unique_links)} unique sections")
        
        for link in unique_links:
            # print(link.get_text(strip=True))
            try:
                # if link.get_text(strip=True) == 'ESN Strasbourg':
                href = link.get('href', '')
                if '/section/' not in href:
                    continue
                
                # Extract accounts platform slug
                accounts_slug = href.split('/section/')[-1].strip('/')
                if not accounts_slug:
                    continue
                
                name = link.get_text(strip=True)
                if not name:
                    continue

                # Get additional details from section page
                section_details = await self.extract_section_details(accounts_slug)
                print(f"\nSection details for {name}:")
                # print(section_details)
                
                # Generate activities platform slug
                activities_slug = generate_activities_slug(name)
                
                section = SectionModel(
                    country_code=country_code.upper(),
                    name=name,
                    accounts_platform_slug=accounts_slug,
                    activities_platform_slug=activities_slug,
                    accounts_url=urljoin(self.base_url, href),
                    activities_url=f"https://activities.esn.org/organisation/{activities_slug}",
                    **section_details
                )
                
                sections.append(section)
                logger.debug(f"Extracted section: {section.name}")
            
            except Exception as e:
                logger.warning(f"Failed to extract section from link {link}: {str(e)}")
                continue
        
        return sections
    
    async def extract_section_details(self, accounts_slug: str) -> Dict[str, Any]:
        """
        Extract detailed information for a specific section.
        
        Args:
            accounts_slug: Section slug on accounts platform
            
        Returns:
            Dictionary with section details
        """
        url = f"{self.base_url}/section/{accounts_slug}"
        print(f"📝 Fetching section details from: {url}")
        
        try:
            content = await self.get_page_content(url)
            soup = await self.parse_html(content, url)
            
            details = {}
            
            # Email
            email_elem = soup.select_one(self.selectors['contact_email'])
            if email_elem:
                details['email'] = email_elem.get_text(strip=True)
            
            # Website
            website_elem = soup.select_one(self.selectors['contact_website'])
            if website_elem:
                details['website'] = website_elem.get('href')
            
            # University name
            university_elem = soup.select_one(self.selectors['university_name'])
            if university_elem:
                details['university_name'] = university_elem.get_text(strip=True)
            
            # Address  
            address_elem = soup.select_one(self.selectors['address'])
            if address_elem:
                address_parts = []
                for span in address_elem.select('span'):
                    text = span.get_text(strip=True)
                    if text:
                        address_parts.append(text)
                details['address'] = ', '.join(address_parts)
            
            # Coordinates
            coords_elem = soup.select_one(self.selectors['coordinates'])
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
            logo_elem = soup.select_one(self.selectors['logo'])
            if logo_elem:
                details['logo_url'] = urljoin(self.base_url, logo_elem.get('src'))
            
            # City
            city_elem = soup.select_one(self.selectors['city'])
            if city_elem:
                details['city'] = city_elem.get_text(strip=True)

            # Social Media
            social_media_links = soup.select(self.selectors['social_media'])
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
            logger.warning(f"Failed to extract details for section {accounts_slug}: {str(e)}")
            return {}
    
    async def validate_activities_slug(self, section: SectionModel) -> bool:
        """
        Validate if activities platform slug is accessible.
        
        Args:
            section: Section model with activities_platform_slug
            
        Returns:
            True if slug is valid, False otherwise
        """
        if not section.activities_platform_slug:
            section.can_scrape_activities = False
            return False
        
        try:
            is_valid = await self.validate_slug_url(
                section.activities_platform_slug,
                "https://activities.esn.org/organisation/{slug}/activities"
            )
            
            section.can_scrape_activities = is_valid
            
            if is_valid:
                logger.debug(f"Activities slug validated: {section.activities_platform_slug}")
            else:
                logger.warning(f"Invalid activities slug: {section.activities_platform_slug}")
                
            return is_valid
            
        except Exception as e:
            logger.error(f"Slug validation error for {section.activities_platform_slug}: {str(e)}")
            section.can_scrape_activities = False
            return False
    
    async def validate_data(self, data: Dict[str, Any]) -> bool:
        """
        Validate scraped data quality.
        
        Args:
            data: Scraped data dictionary
            
        Returns:
            True if data meets quality criteria
        """
        try:
            # Check minimum countries
            if data.get("countries_processed", 0) < 40:
                logger.warning("Too few countries processed")
                return False
            
            # Check minimum sections
            if data.get("sections_processed", 0) < 400:
                logger.warning("Too few sections processed")
                return False
            
            # Check validation rate
            processed = data.get("sections_processed", 0)
            validated = data.get("sections_validated", 0)
            
            if processed > 0:
                validation_rate = validated / processed
                if validation_rate < 0.7:  # At least 70% should be valid
                    logger.warning(f"Low validation rate: {validation_rate:.2%}")
                    return False
            
            # Check error rate
            error_count = len(data.get("errors", []))
            if error_count > processed * 0.1:  # Max 10% errors
                logger.warning(f"Too many errors: {error_count}")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Data validation failed: {str(e)}")
            return False 
        
# SELECT * FROM sections WHERE name = 'ESN Lille';]