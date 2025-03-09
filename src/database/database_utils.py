import psycopg2
from psycopg2 import sql
import json
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def get_db_connection(db_config):
    """
    Establish a connection to the PostgreSQL database.
    
    Args:
        db_config (dict): Database connection parameters
        
    Returns:
        connection: PostgreSQL database connection
    """
    try:
        conn = psycopg2.connect(**db_config)
        logger.info("Database connection established successfully")
        return conn
    except Exception as e:
        logger.error(f"Error connecting to database: {e}")
        return None

def create_tables_if_not_exist(conn):
    """
    Create the database tables if they don't already exist.
    
    Args:
        conn: PostgreSQL database connection
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        cursor = conn.cursor()
        
        # Create Organisations table with enriched fields
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS organisations (
            organisation_id VARCHAR(255) PRIMARY KEY,
            organisation_name VARCHAR(255) NOT NULL,
            country_code VARCHAR(10),
            city VARCHAR(255),
            country VARCHAR(255),
            email VARCHAR(255),
            website VARCHAR(255),
            longitude VARCHAR(100),
            university_name TEXT,
            university_website VARCHAR(255),
            social_media JSONB,
            activity_count INTEGER,
            city_count INTEGER,
            participant_count INTEGER
        )
        """)
        
        # Create Statistics table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS statistics (
            organisation_id VARCHAR(255) PRIMARY KEY,
            total_physical_activities INTEGER,
            total_online_activities INTEGER,
            local_students_participants INTEGER,
            international_students_participants INTEGER,
            coordinators_participants INTEGER,
            total_participants INTEGER,
            environmental_sustainability_activities INTEGER,
            social_inclusion_activities INTEGER,
            culture_activities INTEGER,
            education_youth_activities INTEGER,
            health_wellbeing_activities INTEGER,
            skills_employability_activities INTEGER,
            physical_activity_types JSONB,
            online_activity_types JSONB,
            FOREIGN KEY (organisation_id) REFERENCES organisations (organisation_id)
        )
        """)
        
        # Create Activities table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS activities (
            activity_id VARCHAR(255) PRIMARY KEY,
            organisation_id VARCHAR(255) NOT NULL,
            activity_title VARCHAR(255) NOT NULL,
            activity_date VARCHAR(100),
            activity_city VARCHAR(255),
            activity_country VARCHAR(255),
            participant_count INTEGER,
            activity_causes VARCHAR(255),
            activity_type VARCHAR(255),
            activity_goal TEXT,
            activity_description TEXT,
            sdg_goals TEXT,
            activity_objectives TEXT,
            activity_organiser VARCHAR(255),
            FOREIGN KEY (organisation_id) REFERENCES organisations (organisation_id)
        )
        """)
        
        conn.commit()
        logger.info("Tables created successfully")
        return True
    except Exception as e:
        conn.rollback()
        logger.error(f"Error creating tables: {e}")
        return False

def insert_organisation_data(conn, organisation_data):
    """
    Insert or update organisation data into the organisations table.
    
    Args:
        conn: PostgreSQL database connection
        organisation_data (dict): Organisation details
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        cursor = conn.cursor()
        query = """
        INSERT INTO organisations (
            organisation_id, organisation_name, 
            country_code, city, country, email, website, longitude, 
            university_name, university_website, social_media,
            activity_count, city_count, participant_count
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (organisation_id) DO UPDATE SET
            organisation_name = EXCLUDED.organisation_name,
            country_code = EXCLUDED.country_code,
            city = EXCLUDED.city,
            country = EXCLUDED.country,
            email = EXCLUDED.email,
            website = EXCLUDED.website,
            longitude = EXCLUDED.longitude,
            university_name = EXCLUDED.university_name,
            university_website = EXCLUDED.university_website,
            social_media = EXCLUDED.social_media,
            activity_count = EXCLUDED.activity_count,
            city_count = EXCLUDED.city_count,
            participant_count = EXCLUDED.participant_count
        """
        
        # Extract university information
        university_name = None
        university_website = None
        if 'university' in organisation_data:
            university_name = organisation_data['university'].get('name', None)
            university_website = organisation_data['university'].get('website', None)
        
        # Extract country from address if available
        country = None
        if 'address' in organisation_data:
            country = organisation_data['address'].get('country', None)
        
        # Extract longitude from location if available
        longitude = None
        if 'location' in organisation_data and 'longitude' in organisation_data['location']:
            longitude = organisation_data['location']['longitude']
        
        cursor.execute(query, (
            organisation_data['organisation_id'],
            organisation_data['organisation_name'],
            organisation_data.get('country_code', None),
            organisation_data.get('city', None),
            country,
            organisation_data.get('email', None),
            organisation_data.get('website', None),
            longitude,
            university_name,
            university_website,
            json.dumps(organisation_data.get('social_media', {})) if 'social_media' in organisation_data else None,
            organisation_data['statistics']['activities'] if 'statistics' in organisation_data else None,
            organisation_data['statistics']['cities'] if 'statistics' in organisation_data else None,
            organisation_data['statistics']['participants'] if 'statistics' in organisation_data else None
        ))
        
        conn.commit()
        logger.info(f"Organisation {organisation_data['organisation_id']} inserted/updated successfully")
        return True
    except Exception as e:
        conn.rollback()
        logger.error(f"Error inserting organisation data: {e}")
        return False

def insert_statistics_data(conn, statistics_data):
    """
    Insert or update statistics data into the statistics table.
    
    Args:
        conn: PostgreSQL database connection
        statistics_data (dict): Statistics information
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        cursor = conn.cursor()
        
        # Extract data from the statistics dictionary, with safe defaults
        general_stats = statistics_data.get('general_statistics', {})
        physical_stats = statistics_data.get('physical_activities_statistics', {'total_activities_by_type': {}})
        online_stats = statistics_data.get('online_activities_statistics', {'total_activities_by_type': {}})
        
        # Get total activities with safe defaults
        total_activities = general_stats.get('total_activities', {})
        # Get causes with safe defaults
        causes = general_stats.get('total_activities_by_cause', {})
        # Get participants with safe defaults
        participants = general_stats.get('total_participants', {})
        
        query = """
        INSERT INTO statistics (
            organisation_id, 
            total_physical_activities,
            total_online_activities,
            local_students_participants,
            international_students_participants,
            coordinators_participants,
            total_participants,
            environmental_sustainability_activities,
            social_inclusion_activities,
            culture_activities,
            education_youth_activities,
            health_wellbeing_activities,
            skills_employability_activities,
            physical_activity_types,
            online_activity_types
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (organisation_id) DO UPDATE SET
            total_physical_activities = EXCLUDED.total_physical_activities,
            total_online_activities = EXCLUDED.total_online_activities,
            local_students_participants = EXCLUDED.local_students_participants,
            international_students_participants = EXCLUDED.international_students_participants,
            coordinators_participants = EXCLUDED.coordinators_participants,
            total_participants = EXCLUDED.total_participants,
            environmental_sustainability_activities = EXCLUDED.environmental_sustainability_activities,
            social_inclusion_activities = EXCLUDED.social_inclusion_activities,
            culture_activities = EXCLUDED.culture_activities,
            education_youth_activities = EXCLUDED.education_youth_activities,
            health_wellbeing_activities = EXCLUDED.health_wellbeing_activities,
            skills_employability_activities = EXCLUDED.skills_employability_activities,
            physical_activity_types = EXCLUDED.physical_activity_types,
            online_activity_types = EXCLUDED.online_activity_types
        """
        
        cursor.execute(query, (
            statistics_data.get('organisation_id', ''),
            total_activities.get('Physical activities', 0),
            total_activities.get('Online activities', 0),
            participants.get('Local students', 0),
            participants.get('International students', 0),
            participants.get('Coordinators', 0),
            participants.get('total', 0),
            causes.get('Environmental Sustainability', 0),
            0,  # Social inclusion not available in the data
            causes.get('Culture', 0),
            causes.get('Education & Youth', 0),
            causes.get('Health & Well-being', 0),
            causes.get('Skills & Employability', 0),
            json.dumps(physical_stats.get('total_activities_by_type', {})),
            json.dumps(online_stats.get('total_activities_by_type', {}))
        ))
        
        conn.commit()
        logger.info(f"Statistics for {statistics_data.get('organisation_id')} inserted/updated successfully")
        return True
    except Exception as e:
        conn.rollback()
        logger.error(f"Error inserting statistics data for {statistics_data.get('organisation_id', 'unknown')}: {e}")
        return False

def insert_activity_data(conn, activity):
    """
    Insert or update a single activity into the activities table.
    
    Args:
        conn: PostgreSQL database connection
        activity (dict): Activity information
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        cursor = conn.cursor()
        
        query = """
        INSERT INTO activities (
            activity_id, organisation_id, activity_title, activity_date,
            activity_city, activity_country, participant_count, activity_causes,
            activity_type, activity_goal, activity_description, sdg_goals,
            activity_objectives, activity_organiser
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (activity_id) DO UPDATE SET
            organisation_id = EXCLUDED.organisation_id,
            activity_title = EXCLUDED.activity_title,
            activity_date = EXCLUDED.activity_date,
            activity_city = EXCLUDED.activity_city,
            activity_country = EXCLUDED.activity_country,
            participant_count = EXCLUDED.participant_count,
            activity_causes = EXCLUDED.activity_causes,
            activity_type = EXCLUDED.activity_type,
            activity_goal = EXCLUDED.activity_goal,
            activity_description = EXCLUDED.activity_description,
            sdg_goals = EXCLUDED.sdg_goals,
            activity_objectives = EXCLUDED.activity_objectives,
            activity_organiser = EXCLUDED.activity_organiser
        """
        
        cursor.execute(query, (
            activity.get('activity_id', ''),
            activity.get('organisation_id', ''),
            activity.get('activity_title', ''),
            activity.get('activity_date', ''),
            activity.get('activity_city', ''),
            activity.get('activity_country', ''),
            activity.get('participant_count', 0),
            activity.get('activity_causes', ''),
            activity.get('activity_type', ''),
            activity.get('activity_goal', ''),
            activity.get('activity_description', ''),
            activity.get('sdg_goals', ''),
            activity.get('activity_objectives', ''),
            activity.get('activity_organiser', '')
        ))
        
        conn.commit()
        logger.info(f"Activity {activity.get('activity_id')} inserted/updated successfully")
        return True
    except Exception as e:
        conn.rollback()
        logger.error(f"Error inserting activity data: {e}")
        return False

def insert_activities_batch(conn, activities_list):
    """
    Insert multiple activities into the database.
    
    Args:
        conn: PostgreSQL database connection
        activities_list (list): List of activity dictionaries
    
    Returns:
        dict: Summary of successful and failed insertions
    """
    successful = 0
    failed = 0
    
    for activity in activities_list:
        if insert_activity_data(conn, activity):
            successful += 1
        else:
            failed += 1
    
    return {
        'total': len(activities_list),
        'successful': successful,
        'failed': failed
    }

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
