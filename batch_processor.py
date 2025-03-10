import json
import time
import logging
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Lock
import queue
from data_processor import process_organisation_data
from pathlib import Path

LOG_FILE_PATH = Path(__file__).parent.parent / "logs" / f"esn_processing_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"

# Create logs directory if it doesn't exist
logs_dir = Path(__file__).parent.parent / "logs"
logs_dir.mkdir(parents=True, exist_ok=True)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE_PATH),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger()

class RateLimiter:
    """Rate limiter for controlling request frequency across threads"""
    def __init__(self, delay):
        self.delay = delay
        self.last_request = time.time()
        self.lock = Lock()
    
    def wait(self):
        with self.lock:
            current_time = time.time()
            time_since_last = current_time - self.last_request
            if time_since_last < self.delay:
                time.sleep(self.delay - time_since_last)
            self.last_request = time.time()

def load_esn_data(file_path):
    """
    Load ESN data from JSON file
    
    Args:
        file_path (str): Path to the JSON file
        
    Returns:
        dict: The loaded JSON data or None if failed
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Failed to load ESN data from {file_path}: {e}")
        return None

def extract_branch_details(esn_data):
    """
    Extract all branch details from the ESN data
    
    Args:
        esn_data (dict): The ESN data
        
    Returns:
        list: List of branch details dictionaries
    """
    branches = []
    
    try:
        countries = esn_data.get("countries", [])
        for country in countries:
            country_name = country.get("name")
            country_code = country.get("code")
            
            country_branches = country.get("branches", [])
            for branch in country_branches:
                if not branch.get("id"):
                    continue
                    
                # Create a copy of the branch data with additional details
                branch_data = {
                    'organisation_id': branch.get("id"),
                    'organisation_name': branch.get("name"),
                    'country_code': branch.get("country_code") or country_code,
                    'city': branch.get("city"),
                    'address': branch.get("address", {}),
                    'university': branch.get("university", {}),
                    'email': branch.get("email"),
                    'website': branch.get("website"),
                    'location': branch.get("location", {}),
                    'social_media': branch.get("social_media", {})
                }
                
                branches.append(branch_data)
    except Exception as e:
        logger.error(f"Error extracting branch details: {e}")
    
    return branches

def process_branch(branch_data, rate_limiter):
    """
    Process a single branch with rate limiting
    
    Args:
        branch_data (dict): Dictionary containing branch details
        rate_limiter (RateLimiter): Rate limiter instance
        
    Returns:
        tuple: (branch_id, result_dict)
    """
    branch_id = branch_data['organisation_id']
    try:
        # Wait for rate limiter before making request
        rate_limiter.wait()
        
        # Add statistical placeholders
        branch_data['statistics'] = {'activities': None, 'cities': None, 'participants': None}
        
        # Process the organization data
        result = process_organisation_data(branch_id, branch_data)
        return branch_id, result
    except Exception as e:
        return branch_id, {"success": False, "message": str(e)}

def process_all_branches_with_details(branch_details, delay=2, max_workers=5):
    """
    Process all branches with their details using parallel threading with rate limiting
    
    Args:
        branch_details (list): List of dictionaries containing branch details
        delay (int): Delay between requests in seconds
        max_workers (int): Maximum number of concurrent threads
        
    Returns:
        dict: Results summary
    """
    total = len(branch_details)
    successful = 0
    failed = 0
    skipped = 0
    
    logger.info(f"Starting to process {total} branches with {max_workers} parallel workers")
    logger.info("Note: Scraping ALL activities for each section without page limits")
    
    # Create rate limiter instance
    rate_limiter = RateLimiter(delay)
    
    # Process branches using thread pool
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Submit all tasks
        future_to_branch = {
            executor.submit(process_branch, branch_data, rate_limiter): branch_data
            for branch_data in branch_details
        }
        
        # Process completed tasks as they finish
        for i, future in enumerate(as_completed(future_to_branch)):
            branch_id, result = future.result()
            
            if result.get("success"):
                successful += 1
                logger.info(f"Successfully processed {branch_id} ({i+1}/{total})")
            else:
                if "already exists" in result.get("message", ""):
                    skipped += 1
                    logger.info(f"Skipped {branch_id} - already exists in database ({i+1}/{total})")
                else:
                    failed += 1
                    logger.warning(f"Failed to process {branch_id}: {result.get('message')} ({i+1}/{total})")
    
    return {
        "total": total,
        "successful": successful,
        "failed": failed,
        "skipped": skipped
    }

if __name__ == "__main__":
    # Path to ESN data file
    esn_data_path = "data/esn_data.json"
    
    # Load ESN data
    esn_data = load_esn_data(esn_data_path)
    
    if not esn_data:
        logger.error("Failed to load ESN data. Exiting.")
        exit(1)
    
    # Extract branch details
    branch_details = extract_branch_details(esn_data)

    if not branch_details:
        logger.error("No branch details found in the data. Exiting.")
        exit(1)
    
    logger.info(f"Found {len(branch_details)} branches to process")
    
    # Process all branches with details
    results = process_all_branches_with_details(branch_details)
    
    logger.info("Batch processing completed")
    logger.info(f"Total: {results['total']}")
    logger.info(f"Successful: {results['successful']}")
    logger.info(f"Failed: {results['failed']}")
    logger.info(f"Skipped: {results['skipped']}")