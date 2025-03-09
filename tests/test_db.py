import psycopg2
from psycopg2 import sql

DB_CONFIG = {'host': 'localhost', 'port': 5432, 'database': 'postgres', 'user': 'postgres', 'password': 'setgeb-vyjqa1-Sughop'}

# Connect to database
conn = psycopg2.connect(**DB_CONFIG)
cursor = conn.cursor()

# Check if tables exist
cursor.execute("""
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'public'
ORDER BY table_name;
""")

tables = cursor.fetchall()
print("Tables in database:")
for table in tables:
    print(f"- {table[0]}")

conn.close()