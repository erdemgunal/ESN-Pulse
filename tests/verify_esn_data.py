import json
import requests
import time
from bs4 import BeautifulSoup
import threading
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime

def verify_no_duplicates(data):
    """Verify there are no duplicate branches in any country."""
    all_clean = True
    
    for country in data["countries"]:
        branch_ids = [branch["id"] for branch in country["branches"]]
        unique_ids = set(branch_ids)
        
        if len(branch_ids) != len(unique_ids):
            all_clean = False
            duplicates = {}
            for branch_id in branch_ids:
                if branch_id in duplicates:
                    duplicates[branch_id] += 1
                else:
                    duplicates[branch_id] = 1
            
            duplicate_ids = [bid for bid, count in duplicates.items() if count > 1]
            print(f"Found duplicates in {country['name']}:")
            for dup_id in duplicate_ids:
                print(f"  - Branch ID '{dup_id}' appears {duplicates[dup_id]} times")
    
    if all_clean:
        print("Verification complete: No duplicate branches found!")
    else:
        print("Verification failed: Found duplicate branches.")
    
    return all_clean

def analyze_data(data):
    """Print statistics about the ESN data."""
    country_count = len(data["countries"])
    branch_count = sum(len(country["branches"]) for country in data["countries"])
    
    print(f"\nESN Data Analysis:")
    print(f"- Total countries: {country_count}")
    print(f"- Total branches: {branch_count}")
    
    # Verify metadata is correct
    if "metadata" in data:
        metadata = data["metadata"]
        metadata_countries = metadata.get("total_countries", "Not specified")
        metadata_branches = metadata.get("total_branches", "Not specified")
        
        print(f"\nMetadata:")
        print(f"- Countries: {metadata_countries} (Actual: {country_count})")
        print(f"- Branches: {metadata_branches} (Actual: {branch_count})")
        
        if metadata_countries != country_count or metadata_branches != branch_count:
            print("WARNING: Metadata doesn't match actual counts!")

def check_url(branch_info, print_lock, log_file):
    """Check a single URL in a thread"""
    branch_id = branch_info["id"]
    url = f"https://activities.esn.org/organisation/{branch_id}"
    
    try:
        response = requests.get(url)
        status = response.status_code
        
        with print_lock:
            print(f"URL: {url} - Status: {status}")
            
            if status == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                title = soup.title.text.strip() if soup.title else "No title"
                print(f"  Title: {title}")
            
            print()
    except Exception as e:
        with print_lock:
            print(f"Error checking {url}: {e}")
            print(f"Failed URL: {url}")
            
            # Log broken URL to file
            with open(log_file, 'a') as f:
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                f.write(f"[{timestamp}] {url} - Error: {e}\n")

def debug_check_urls(data):
    """Debug function to check if URLs for problematic branches actually work using threads"""
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

    print_lock = threading.Lock()
    max_workers = 10  # Adjust based on system capabilities
    
    # Create log file with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = f"/Users/erdemgunal/Desktop/sites/esn/ESN Pulse/logs/broken_urls_{timestamp}.log"
    
    # Ensure logs directory exists
    import os
    os.makedirs(os.path.dirname(log_file), exist_ok=True)
    
    print(f"Checking {len(all_branches)} URLs using {max_workers} threads...")
    print(f"Broken URLs will be logged to: {log_file}")
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Submit tasks to the thread pool
        for branch_info in all_branches:
            executor.submit(check_url, branch_info, print_lock, log_file)

def main():
    # Load ESN data
    file_path = '/Users/erdemgunal/Desktop/sites/esn/ESN Pulse/data/esn_data.json'
    
    with open(file_path, 'r') as f:
        data = json.load(f)
    
    # # Verify no duplicates
    # verify_no_duplicates(data)
    
    # # Analyze the data
    # analyze_data(data)

    # debug links
    debug_check_urls(data)

if __name__ == "__main__":
    main()