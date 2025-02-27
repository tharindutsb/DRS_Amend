import configparser
from pymongo import MongoClient
import os
import logging
import time

# Setup logging
logging.basicConfig(level=logging.DEBUG)  # Set to DEBUG
logger = logging.getLogger(__name__)

DB_CONFIG_FILE = "DB_Config.ini"

def get_db_connection():
    # Ensure DB_Config.ini exists
    if not os.path.exists(DB_CONFIG_FILE):
        logger.error(f"Configuration file {DB_CONFIG_FILE} not found.")
        return None

    # Read configuration file
    config = configparser.ConfigParser()
    config.read(DB_CONFIG_FILE)

    if "DATABASE" not in config:
        logger.error("'DATABASE' section missing in DB_Config.ini")
        return None

    mongo_uri = config["DATABASE"].get("MONGO_URI", "mongodb://localhost:27017").strip()
    db_name = config["DATABASE"].get("DB_NAME", "intern_db").strip()

    if not mongo_uri or not db_name:
        logger.error(" Missing MONGO_URI or DB_NAME in DB_Config.ini")
        return None

    # Retry connection with error logging
    for attempt in range(3):
        try:
            client = MongoClient(mongo_uri, serverSelectionTimeoutMS=5000)
            db = client[db_name]

            # Test connection
            client.server_info()
            logger.info(f"Connected to MongoDB successfully: {db_name}")
            return db
        except Exception as e:
            logger.error(f" Error connecting to MongoDB (Attempt {attempt+1}): {e}")
            time.sleep(2)  # Wait before retrying

    logger.error(" Failed to connect to MongoDB after multiple attempts.")
    return None
