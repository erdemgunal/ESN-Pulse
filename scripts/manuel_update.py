import json
import requests
import time
from pathlib import Path
from bs4 import BeautifulSoup
from datetime import datetime
import os
from urllib.parse import urlparse, urlunparse
import threading
import unicodedata

# Path to the ESN data file and log file
DATA_FILE_PATH = Path(__file__).parent.parent / "data" / "esn_data.json"
LOG_FILE_PATH = Path(__file__).parent.parent / "logs" / f"problematic_branches_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"

# Create logs directory if it doesn't exist
os.makedirs(os.path.dirname(LOG_FILE_PATH), exist_ok=True)

# Thread-safe logging
log_lock = threading.Lock()

def log_message(message):
    """Log messages to the log file in a thread-safe way"""
    with log_lock:
        with open(LOG_FILE_PATH, 'a', encoding='utf-8') as log_file:
            log_file.write(f"{datetime.now().isoformat()}: {message}\n")

# Problematic branches with their normalized names and correct IDs
problematic_branches = [
    {"search_name": "ESN - New Bulgarian University", "id": "esn-new-bulgarian-university"},
    {"search_name": "ESN Ostravská", "id": "esn-vsb-tu-ostrava"},
    {"search_name": "Autour du Monde - ESN Nantes", "id": "autour-du-monde-esn-nantes"},
    {"search_name": "ESN BISE - Saint-Etienne", "id": "esn-bise-saint-etienne"},
]

def normalize_text(text):
    """Normalize text by removing accents and converting to lowercase"""
    # Normalize Unicode characters and convert to lowercase
    return unicodedata.normalize('NFKD', text).encode('ASCII', 'ignore').decode('ASCII').lower()

def normalize_branch_name(name):
    """Normalize branch name for better matching"""
    # Remove common prefixes and suffixes, normalize spaces, etc.
    name = name.replace("ESN ", "").replace(" e.V.", "").replace("(", "").replace(")", "")
    return normalize_text(name.strip())

def clean_social_media_url(url):
    """Clean social media URLs by removing query parameters"""
    try:
        parsed_url = urlparse(url)
        # Return the URL without query parameters
        return urlunparse((parsed_url.scheme, parsed_url.netloc, parsed_url.path, '', '', ''))
    except Exception as e:
        message = f"Error cleaning URL {url}: {e}"
        print(message)
        log_message(message)
        return url

def extract_all_social_media(soup):
    """Extract all social media links from HTML content"""
    # Dictionary to store social media links
    social_media = {}
    
    # Look for Facebook link
    facebook_link = soup.select_one('.organisation__field-org-facebook a')
    if (facebook_link):
        social_media['facebook'] = facebook_link.get('href')
    
    # Look for Instagram link
    instagram_link = soup.select_one('.organisation__field-org-instagram a')
    if (instagram_link):
        social_media['instagram'] = instagram_link.get('href')
    
    # Look for all social media links generically
    social_links = soup.select('a[href*="facebook.com"], a[href*="instagram.com"], a[href*="twitter.com"], a[href*="linkedin.com"], a[href*="x.com"]')
    
    for link in social_links:
        href = link.get('href', '')
        if 'facebook.com' in href and 'facebook' not in social_media:
            social_media['facebook'] = href
        elif 'instagram.com' in href and 'instagram' not in social_media:
            social_media['instagram'] = href
        elif 'twitter.com' in href or 'x.com' in href:
            social_media['twitter'] = href
        elif 'linkedin.com' in href:
            social_media['linkedin'] = href
    
    return social_media

def scrape_social_media(branch_id):
    """Scrape social media accounts for a branch using its ID"""
    url = f"https://activities.esn.org/organisation/{branch_id}"
    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Sec-Fetch-Site': 'none',
        'Sec-Fetch-Mode': 'navigate',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.1.1 Safari/605.1.15',
        'Accept-Language': 'en-US,en;q=0.9',
        'Sec-Fetch-Dest': 'document',
        'Priority': 'u=0, i',
    }
    
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            social_accounts = extract_all_social_media(soup)
            print(f"Successfully accessed {url} and found {len(social_accounts)} social accounts")
            return social_accounts
        else:
            message = f"Failed to access {url} (Status: {response.status_code})"
            print(message)
            log_message(message)
            return {}
    except Exception as e:
        message = f"Error scraping {url}: {e}"
        print(message)
        log_message(message)
        return {}

def find_branch_by_name(data, search_name):
    """Find a branch in the data by its name, using flexible matching"""
    normalized_search = normalize_text(search_name)
    
    best_match = None
    best_match_score = 0
    
    for country in data["countries"]:
        for branch in country["branches"]:
            branch_name = branch["name"]
            
            # Check for exact match
            if branch_name == search_name:
                return branch, country["branches"].index(branch), data["countries"].index(country)
            
            # Check for case-insensitive match
            if branch_name.lower() == search_name.lower():
                return branch, country["branches"].index(branch), data["countries"].index(country)
            
            # Check for normalized match
            branch_norm = normalize_text(branch_name)
            if branch_norm == normalized_search:
                return branch, country["branches"].index(branch), data["countries"].index(country)
            
            # Calculate similarity score
            shorter, longer = (branch_norm, normalized_search) if len(branch_norm) < len(normalized_search) else (normalized_search, branch_norm)
            if shorter in longer:
                score = len(shorter) / len(longer)
                if score > best_match_score:
                    best_match_score = score
                    best_match = (branch, country["branches"].index(branch), data["countries"].index(country))
    
    # Return the best partial match if score is high enough
    if best_match_score > 0.7:
        return best_match
    
    return None, -1, -1

def update_problematic_branches():
    """Update problematic branches and scrape their social media accounts"""
    # Load the JSON data
    with open(DATA_FILE_PATH, 'r', encoding='utf-8') as file:
        data = json.load(file)
    
    # Counters for tracking updates
    updated_id_count = 0
    social_media_count = 0
    
    # Process each problematic branch
    for problem in problematic_branches:
        search_name = problem["search_name"]
        correct_id = problem["id"]
        
        print(f"Processing problematic branch: {search_name}")
        branch, branch_index, country_index = find_branch_by_name(data, search_name)
        
        if branch_index == -1:
            message = f"Could not find branch: {search_name} in the data"
            print(message)
            log_message(message)
            continue
        
        # Update the branch ID
        old_id = branch.get("id", "")
        if old_id != correct_id:
            branch["id"] = correct_id
            branch["url"] = f"/organisation/{correct_id}"
            updated_id_count += 1
            print(f"Updated ID for {branch['name']}: {old_id} -> {correct_id}")
        
        # Try to scrape social media accounts
        print(f"Scraping social media for {branch['name']} with ID: {correct_id}")
        social_accounts = scrape_social_media(correct_id)
        
        if social_accounts:
            if "social_media" not in branch:
                branch["social_media"] = {}
            
            # Update social media accounts
            for platform, url in social_accounts.items():
                clean_url = clean_social_media_url(url)
                branch["social_media"][platform] = clean_url
                social_media_count += 1
            
            print(f"Added {len(social_accounts)} social media accounts for {branch['name']}")
        else:
            print(f"No social media accounts found for {branch['name']}")
        
        # Add a delay to avoid overloading the server
        time.sleep(2)
    
    # Save the updated data
    with open(DATA_FILE_PATH, 'w', encoding='utf-8') as file:
        json.dump(data, file, indent=2, ensure_ascii=False)
    
    print(f"Update complete. Updated {updated_id_count} branch IDs and added {social_media_count} social media accounts.")

def debug_check_urls():
    """Debug function to check if URLs for problematic branches actually work"""
    for problem in problematic_branches:
        branch_id = problem["id"]
        url = f"https://activities.esn.org/organisation/{branch_id}"
        
        try:
            response = requests.get(url)
            status = response.status_code
            print(f"URL: {url} - Status: {status}")
            
            if status == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                title = soup.title.text.strip() if soup.title else "No title"
                print(f"  Title: {title}")
                
                social = extract_all_social_media(soup)
                print(f"  Social accounts: {len(social)}")
                for platform, link in social.items():
                    print(f"    {platform}: {link}")
            
            print()
        except Exception as e:
            print(f"Error checking {url}: {e}")
        
        time.sleep(1)

if __name__ == "__main__":
    # First debug the URLs to make sure they work
    # print("Debugging URLs for problematic branches...")
    # debug_check_urls()
    
    print("\nUpdating problematic branches...")
    update_problematic_branches()