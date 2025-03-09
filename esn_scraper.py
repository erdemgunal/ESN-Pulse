import os
import json
import time
import datetime
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from typing import Dict, List, Optional

class ESNScraper:
    """
    Scraper class for ESN Accounts website to extract countries and sections
    """
    
    BASE_URL = "https://accounts.esn.org"
    
    def __init__(self, delay: float = 1.0):
        """
        Initialize the scraper
        Args:
            delay: Delay between requests in seconds to avoid overloading the server
        """
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) ESN Data Collection/1.0'
        })
        self.delay = delay
        self.countries = []
        self.last_request_time = 0
        
    def _get_page(self, url: str) -> str:
        """
        Get page content from URL with rate limiting
        Args:
            url: Page URL (absolute or relative)
        """
        # Rate limiting
        elapsed = time.time() - self.last_request_time
        if elapsed < self.delay:
            time.sleep(self.delay - elapsed)
            
        full_url = urljoin(self.BASE_URL, url)
        print(f"Fetching {full_url}")
        
        try:
            response = self.session.get(full_url)
            response.raise_for_status()
            self.last_request_time = time.time()
            return response.text
        except requests.RequestException as e:
            print(f"Error fetching {full_url}: {e}")
            # Wait a bit longer on error
            time.sleep(self.delay * 2)
            return ""
    
    def scrape_countries(self) -> List[Dict]:
        """Scrape all ESN countries from the welcome page"""
        welcome_page = self._get_page("/")
        if not welcome_page:
            print("Failed to fetch welcome page")
            return []
            
        soup = BeautifulSoup(welcome_page, 'html.parser')
        countries = []
        country_rows = soup.select('.country-list-row')
        
        for row in country_rows:
            link = row.select_one('.views-field-label a')
            if link:
                country_name = link.text.strip()
                url = link.get('href')
                
                # Extract country code from URL or flag class
                country_code = None
                flag_span = row.select_one(".country-list.flag-icon")
                if flag_span:
                    flag_classes = flag_span.get('class', [])
                    for cls in flag_classes:
                        if cls.startswith('flag-icon-'):
                            country_code = cls.replace('flag-icon-', '')
                            break
                    
                if not country_code and url:
                    country_code = url.split('/')[-1]
                
                countries.append({
                    'name': country_name,
                    'code': country_code,
                    'url': url,
                    'branches': []
                })
        
        self.countries = countries
        return countries
    
    def scrape_branches_for_country(self, country: Dict) -> List[Dict]:
        """
        Scrape all branches for a specific country
        Args:
            country: Country dictionary with name, code and url
        """
        country_code = country['code']
        country_url = country['url']
        
        try:
            country_page = self._get_page(country_url)
            if not country_page:
                return []
                
            soup = BeautifulSoup(country_page, 'html.parser')
            
            # Extract number of sections if available
            sections_header = soup.select_one('.view-header .num_sections_country')
            if sections_header:
                sections_text = sections_header.text.strip()
                num_sections = int(sections_text.split(':')[1].strip()) if ':' in sections_text else 0
                print(f"Found {num_sections} sections for {country['name']}")
            
            branches = []
            branch_links = soup.select('.views-field-label a')
            
            for link in branch_links:
                branch_name = link.text.strip()
                branch_url = link.get('href')
                branch_id = branch_url.split('/')[-1] if branch_url else None
                
                branch = {
                    'name': branch_name,
                    'id': branch_id,
                    'url': branch_url,
                    'country_code': country_code
                }
                
                branches.append(branch)
                
            country['branches'] = branches
            return branches
            
        except Exception as e:
            print(f"Error scraping branches for {country['name']}: {e}")
            return []
            
    def scrape_branch_details(self, branch: Dict) -> Dict:
        """
        Scrape detailed information for a specific branch
        Args:
            branch: Branch dictionary with name, id and url
        """
        branch_url = branch['url']
        
        try:
            branch_page = self._get_page(branch_url)
            if not branch_page:
                return branch
                
            soup = BeautifulSoup(branch_page, 'html.parser')
            
            # Extract city
            city_elem = soup.select_one('.field--name-field-city .field--item')
            if city_elem:
                branch['city'] = city_elem.text.strip()
                
            # Extract address
            address_elem = soup.select_one('.field--name-field-address .address')
            if address_elem:
                address = {}
                address_line1 = address_elem.select_one('.address-line1')
                address_line2 = address_elem.select_one('.address-line2')
                postal_code = address_elem.select_one('.postal-code')
                locality = address_elem.select_one('.locality')
                country = address_elem.select_one('.country')
                
                if address_line1:
                    address['line1'] = address_line1.text.strip()
                if address_line2:
                    address['line2'] = address_line2.text.strip()
                if postal_code:
                    address['postal_code'] = postal_code.text.strip()
                if locality:
                    address['locality'] = locality.text.strip()
                if country:
                    address['country'] = country.text.strip()
                    
                branch['address'] = address
                
            # Extract university details
            university_name = soup.select_one('.field--name-field-university-name .field--item')
            university_website = soup.select_one('.field--name-field-university-website .field--item a')
            
            if university_name or university_website:
                university = {}
                
                if university_name:
                    university['name'] = university_name.text.strip()
                    
                if university_website:
                    university['website'] = university_website.get('href')
                    
                branch['university'] = university
                
            # Extract email
            email_elem = soup.select_one('.field--name-field-email .field--item')
            if email_elem:
                branch['email'] = email_elem.text.strip()
                
            # Extract website
            # Try different CSS selectors that might match the website link
            website_selectors = [
                '.__[class*="mt"] a[title="Website of the organisation"]',
                '.mt-3 a[title*="Website"]',
                'a[href*="://"][target="_blank"]'
            ]
            
            for selector in website_selectors:
                website_elem = soup.select_one(selector)
                if website_elem and 'href' in website_elem.attrs:
                    branch['website'] = website_elem.get('href')
                    break
                
            # Extract location coordinates
            location_elem = soup.select_one('.geolocation-location')
            if location_elem:
                lat = location_elem.get('data-lat')
                lng = location_elem.get('data-lng')
                
                if lat and lng:
                    branch['location'] = {
                        'latitude': lat,
                        'longitude': lng
                    }
                    
            return branch
            
        except Exception as e:
            print(f"Error scraping details for {branch['name']}: {e}")
            return branch
            
    def scrape_all(self, with_branch_details: bool = True) -> Dict:
        """
        Scrape all countries and their branches
        Args:
            with_branch_details: Whether to fetch detailed information for each branch
        """
        print("Scraping countries...")
        countries = self.scrape_countries()
        
        result = {
            "metadata": {
                "total_countries": len(countries),
                "total_branches": 0,
                "scrape_date": datetime.datetime.now().isoformat()
            },
            "countries": []
        }
        
        for i, country in enumerate(countries):
            print(f"Scraping branches for {country['name']} ({i+1}/{len(countries)})...")
            branches = self.scrape_branches_for_country(country)
            
            if with_branch_details and branches:
                for j, branch in enumerate(branches):
                    print(f"  Scraping details for {branch['name']} ({j+1}/{len(branches)})...")
                    self.scrape_branch_details(branch)
            
            result["countries"].append(country)
            result["metadata"]["total_branches"] += len(branches)
            
        return result
        
    def save_to_json(self, data: Dict, output_path: str):
        """Save scraped data to a JSON file"""
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"Data saved to {output_path}")


if __name__ == "__main__":
    # Example usage
    output_file = os.path.join(os.path.dirname(__file__), "esn_data.json")
    
    print("Running ESN Scraper directly...")
    # print(output_file)
    scraper = ESNScraper(delay=2.0)  # 2 second delay between requests
    data = scraper.scrape_all(with_branch_details=True)
    scraper.save_to_json(data, output_file)
    
    print(f"Scraped {len(data['countries'])} countries with {data['metadata']['total_branches']} branches.")