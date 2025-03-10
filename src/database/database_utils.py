import logging
from .db_setup import get_db_connection, create_tables_if_not_exist
from .db_operations import (
    insert_organisation_data,
    insert_statistics_data,
    insert_activity_data,
    insert_activities_batch
)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def save_scraped_data(db_config, organisation_data, statistics_data, activities_list):
    """
    Main function to save all scraped data to the database.
    
    Args:
        db_config (dict): Database configuration parameters
        organisation_data (dict): Organisation details
        statistics_data (dict): Statistics information
        activities_list (list): List of activity dictionaries
    
    Returns:
        dict: Operation result summary
    """
    # Establish database connection
    conn = get_db_connection(db_config)
    if not conn:
        return {'success': False, 'message': 'Failed to establish database connection'}
    
    try:
        # Create tables if they don't exist
        if not create_tables_if_not_exist(conn):
            return {'success': False, 'message': 'Failed to create database tables'}
        
        # Insert organisation data
        org_result = insert_organisation_data(conn, organisation_data)
        if not org_result:
            return {'success': False, 'message': 'Failed to insert organisation data'}
        
        # Insert statistics data
        stats_result = insert_statistics_data(conn, statistics_data)
        if not stats_result:
            return {'success': False, 'message': 'Failed to insert statistics data'}
        
        # Insert activities data
        activities_result = insert_activities_batch(conn, activities_list)
        
        return {
            'success': True,
            'organisation': {'id': organisation_data['organisation_id'], 'status': 'success'},
            'statistics': {'id': statistics_data['organisation_id'], 'status': 'success'},
            'activities': activities_result
        }
    
    finally:
        # Always close the connection
        if conn:
            conn.close()
            logger.info("Database connection closed")
