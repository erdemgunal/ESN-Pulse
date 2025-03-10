import psycopg2
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
