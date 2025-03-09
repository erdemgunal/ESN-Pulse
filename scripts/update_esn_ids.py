import json
import requests
import time
import re
from pathlib import Path
from bs4 import BeautifulSoup
from datetime import datetime
import os
from urllib.parse import urlparse, urlunparse
import concurrent.futures
import threading

# Path to the ESN data file and log file
DATA_FILE_PATH = Path(__file__).parent.parent / "data" / "esn_data.json"
LOG_FILE_PATH = Path(__file__).parent.parent / "logs" / f"access_failures_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"

# Create logs directory if it doesn't exist
os.makedirs(os.path.dirname(LOG_FILE_PATH), exist_ok=True)

# Thread-safe logging
log_lock = threading.Lock()

def log_failure(message):
    """Log failures to the log file in a thread-safe way"""
    with log_lock:
        with open(LOG_FILE_PATH, 'a', encoding='utf-8') as log_file:
            log_file.write(f"{datetime.now().isoformat()}: {message}\n")

def slugify_name(name):
    """Convert a name to URL-friendly format by replacing spaces with hyphens and lowercasing"""
    return name.lower().replace(' ', '-')

def clean_social_media_url(url):
    """Clean social media URLs by removing query parameters"""
    try:
        parsed_url = urlparse(url)
        # Return the URL without query parameters
        return urlunparse((parsed_url.scheme, parsed_url.netloc, parsed_url.path, '', '', ''))
    except Exception as e:
        print(f"Error cleaning URL {url}: {e}")
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

def check_branch_url(branch_info):
    """Check if a branch URL exists and return the ID and social media accounts if it does"""
    branch_name = branch_info["name"]
    branch_id = branch_info.get("id", "")
    
    # Create URL-friendly name
    url_name = slugify_name(branch_name)
    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Sec-Fetch-Site': 'none',
        'Sec-Fetch-Mode': 'navigate',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.1.1 Safari/605.1.15',
        'Accept-Language': 'en-US,en;q=0.9',
        'Sec-Fetch-Dest': 'document',
        'Priority': 'u=0, i',
    }
    url = f"https://activities.esn.org/organisation/{url_name}"
    
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            social_accounts = extract_all_social_media(soup)
            print(f"Found {branch_name}: {url_name} with {len(social_accounts)} social accounts")
            return {
                "original_id": branch_id,
                "name": branch_name,
                "id": url_name, 
                "social": social_accounts
            }
        else:
            message = f"Failed to access {url} (Status: {response.status_code})"
            print(message)
            log_failure(message)
            return {
                "original_id": branch_id,
                "name": branch_name,
                "id": branch_id,
                "social": {}
            }
    except Exception as e:
        message = f"Error checking URL {url}: {e}"
        print(message)
        log_failure(message)
        return {
            "original_id": branch_id,
            "name": branch_name,
            "id": branch_id,
            "social": {}
        }

def update_branch_ids():
    """Update branch IDs in the ESN data file using threading"""
    # Load the JSON data
    with open(DATA_FILE_PATH, 'r', encoding='utf-8') as file:
        data = json.load(file)
    
    # Counters for tracking changes
    updated_count = 0
    social_media_count = 0
    
    # Collect all branches from all countries for parallel processing
    all_branches = []
    for country in data["countries"]:
        for branch in country["branches"]:
            branch_info = {
                "name": branch["name"],
                "id": branch.get("id", ""),
                "country_index": data["countries"].index(country),
                "branch_index": country["branches"].index(branch)
            }
            all_branches.append(branch_info)
    
    # Process branches in parallel
    branch_results = []
    
    # Define the maximum number of workers (adjust based on your system)
    max_workers = 10
    
    # Use ThreadPoolExecutor for parallel processing
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Submit all branch checks to the executor
        future_to_branch = {executor.submit(check_branch_url, branch): branch for branch in all_branches}
        
        # Process results as they complete
        for future in concurrent.futures.as_completed(future_to_branch):
            branch_info = future_to_branch[future]
            try:
                result = future.result()
                if result:
                    branch_results.append({
                        "country_index": branch_info["country_index"],
                        "branch_index": branch_info["branch_index"],
                        "result": result
                    })
            except Exception as e:
                message = f"Error processing branch {branch_info['name']}: {e}"
                print(message)
                log_failure(message)
    
    # Update data with results
    for branch_result in branch_results:
        country_index = branch_result["country_index"]
        branch_index = branch_result["branch_index"]
        result = branch_result["result"]
        
        branch = data["countries"][country_index]["branches"][branch_index]
        
        # Update ID if different
        if result["id"] != result["original_id"]:
            print(f"Updating {result['name']}: {result['original_id']} -> {result['id']}")
            branch["id"] = result["id"]
            branch["url"] = f"/organisation/{result['id']}"
            updated_count += 1
        
        # Add social media accounts
        if result["social"]:
            if "social_media" not in branch:
                branch["social_media"] = {}
            
            # Update each social media account with cleaned URLs
            for platform, url in result["social"].items():
                clean_url = clean_social_media_url(url)
                if url != clean_url:
                    print(f"Cleaned URL: {url} -> {clean_url}")
                branch["social_media"][platform] = clean_url
                social_media_count += 1
    
    # Save the updated data back to file
    with open(DATA_FILE_PATH, 'w', encoding='utf-8') as file:
        json.dump(data, file, indent=2, ensure_ascii=False)
    
    print(f"Update complete. Updated {updated_count} branch IDs and added {social_media_count} social media accounts.")

if __name__ == "__main__":
    update_branch_ids()