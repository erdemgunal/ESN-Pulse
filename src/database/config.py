# Database configuration parameters
# Modify these values according to your PostgreSQL setup
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

print("config.py executed")
print(DB_CONFIG)