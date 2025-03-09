from src.database.database_utils import save_scraped_data, get_db_connection
from src.database.config import DB_CONFIG
from src.scraping.statistics_scraper import StatisticsScraper
from src.scraping.organisations_scraper import OrganisationsScraper
from src.scraping.activities_scraper import ActivitiesScraper
import logging

# Configure logging for this module
logger = logging.getLogger(__name__)

def check_organisation_exists(organisation_id):
    """
    Check if the organisation already exists in the database with complete data.
    
    Args:
        organisation_id (str): The ESN organisation ID
        
    Returns:
        bool: True if organisation exists with complete data, False otherwise
    """
    conn = get_db_connection(DB_CONFIG)
    if not conn:
        return False
        
    try:
        cursor = conn.cursor()
        
        # Check if organisation exists with activities
        query = """
        SELECT o.organisation_id, 
               (SELECT COUNT(*) FROM activities a WHERE a.organisation_id = o.organisation_id) as activity_count,
               (SELECT COUNT(*) FROM statistics s WHERE s.organisation_id = o.organisation_id) as has_statistics
        FROM organisations o 
        WHERE o.organisation_id = %s
        """
        
        cursor.execute(query, (organisation_id,))
        result = cursor.fetchone()
        
        if result:
            org_id, activities_count, has_statistics = result
            # Return True only if organisation exists with activities and statistics
            return activities_count > 0 and has_statistics > 0
            
        return False
        
    except Exception as e:
        logger.error(f"Error checking organisation existence: {e}")
        return False
    finally:
        conn.close()

def process_organisation_data(organisation_id, organisation_details=None):
    """
    Process and save data for a specific organisation.
    
    Args:
        organisation_id (str): The ESN organisation ID
        organisation_details (dict, optional): Pre-loaded organisation details from JSON
        
    Returns:
        dict: Operation results
    """
    logger.info(f"Processing data for organisation: {organisation_id}")
    
    # Check if organisation already exists in database with complete data
    if check_organisation_exists(organisation_id):
        logger.info(f"Organisation {organisation_id} already exists in database with complete data. Skipping processing.")
        return {"success": True, "message": "already exists", "skip_reason": "complete_data_exists"}
    
    # 1. Use provided details or scrape organisation details
    if organisation_details and organisation_details.get('organisation_id') == organisation_id:
        organisation_data = organisation_details
        logger.info(f"Using pre-loaded details for {organisation_id}")
    else:
        # Scrape organisation details
        org_scraper = OrganisationsScraper()
        organisation_data = org_scraper.scrape_organisation_details(organisation_id)
        if not organisation_data:
            return {"success": False, "message": f"Failed to scrape organisation details for {organisation_id}"}
    
    # 2. Scrape statistics
    stats_scraper = StatisticsScraper()
    statistics_data = stats_scraper.scrape_statistics(organisation_id)
    if not statistics_data:
        return {"success": False, "message": f"Failed to scrape statistics for {organisation_id}"}
    
    # Handle statistics data safely to avoid KeyErrors
    try:
        # Update organisation data with freshly scraped statistics if needed
        if 'statistics' not in organisation_data or not all(organisation_data['statistics'].values()):
            general_stats = statistics_data.get('general_statistics', {})
            
            # Calculate total activities from the sum of physical and online if total_activities_count is missing
            total_activities = general_stats.get('total_activities_count', 0)
            if not total_activities:
                activities_dict = general_stats.get('total_activities', {})
                physical = activities_dict.get('Physical activities', 0)
                online = activities_dict.get('Online activities', 0)
                total_activities = physical + online
            
            # Extract other statistics with safe defaults
            cities_count = general_stats.get('cities_count', 0)
            participants = general_stats.get('total_participants', {}).get('total', 0)
            
            organisation_data['statistics'] = {
                'activities': total_activities,
                'cities': cities_count,
                'participants': participants
            }
            
            logger.info(f"Updated statistics for {organisation_id}: activities={total_activities}, cities={cities_count}, participants={participants}")
    except Exception as e:
        logger.error(f"Error processing statistics for {organisation_id}: {e}")
        # Continue with processing, even if statistics update fails
    
    # 3. Scrape activities - no max_pages parameter to get all activities
    activities_scraper = ActivitiesScraper()
    logger.info(f"Getting all activities for {organisation_id} without page limits")
    activities_data = activities_scraper.get_all_organisation_activities(organisation_id)
    if not activities_data:
        logger.warning(f"No activities found for {organisation_id}, continuing with empty activities list")
        activities_data = []  # Continue with empty activities rather than failing
    else:
        logger.info(f"Found {len(activities_data)} activities for {organisation_id}")
    
    # 4. Save all data to database
    result = save_scraped_data(
        DB_CONFIG, 
        organisation_data, 
        statistics_data, 
        activities_data
    )
    
    return result