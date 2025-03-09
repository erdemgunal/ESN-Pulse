import psycopg2
import matplotlib.pyplot as plt

# Database configuration
from dotenv import load_dotenv
import os
load_dotenv()

DB_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "database": os.getenv("DB_NAME"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASS")
}

def visualize_activity_counts_by_city(db_config):
    """
    Connects to the PostgreSQL database, fetches activity counts per city,
    and visualizes the data using a bar chart.
    """
    try:
        # Establish database connection
        conn = psycopg2.connect(**db_config)
        cursor = conn.cursor()

        # Execute query to get activity counts per city
        cursor.execute("""
            SELECT activity_city, COUNT(*)
            FROM activities
            GROUP BY activity_city
        """)

        # Fetch the data
        data = cursor.fetchall()

        # Prepare data for plotting
        cities = [row[0] for row in data]
        counts = [row[1] for row in data]

        # Create the bar chart
        plt.figure(figsize=(10, 6))  # Adjust figure size as needed
        plt.bar(cities, counts)
        plt.xlabel("City")
        plt.ylabel("Activity Count")
        plt.title("Activity Counts by City")
        plt.xticks(rotation=45, ha="right")  # Rotate city names for readability
        plt.tight_layout()  # Adjust layout to prevent labels from overlapping

        # Show the plot
        plt.show()

    except Exception as e:
        print(f"Error: {e}")
    finally:
        # Close the connection
        if conn:
            cursor.close()
            conn.close()

if __name__ == "__main__":
    visualize_activity_counts_by_city(DB_CONFIG)