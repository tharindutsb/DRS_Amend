import configparser
from pymongo import MongoClient
import os
from utils.loggers import get_logger

# Collection names
CASE_COLLECTION = "DRS.Tmp_Case_Distribution_DRC"
TRANSACTION_COLLECTION = "Case_distribution_drc_transactions"
CASE_DRC_SUMMARY = "DRS_Database.Case_Distribution_DRC_Summary"
SYSTEM_TASKS = "System_tasks"
TEMPLATE_TASK = "Template_task"

# Initialize logger
logger = get_logger("database_logger")

def get_db_connection():
    config_path = os.path.join(os.path.dirname(__file__), "../Config/DB_Config.ini")

    if not os.path.exists(config_path):
        logger.error(f"Configuration file '{config_path}' not found.")
        return None

    config = configparser.ConfigParser()
    config.read(config_path)

    if 'DATABASE' not in config:
        logger.error("'DATABASE' section not found in DB_Config.ini")
        return None

    mongo_uri = config['DATABASE'].get('MONGO_URI', '').strip()
    db_name = config['DATABASE'].get('DB_NAME', '').strip()

    if not mongo_uri or not db_name:
        logger.error("Missing MONGO_URI or DB_NAME in DB_Config.ini")
        return None

    try:
        client = MongoClient(mongo_uri)
        db = client[db_name]
        return db
    except Exception as e:
        logger.error(f"Error connecting to MongoDB: {e}")
        return None

def get_collection(collection_name):
    """
    Returns a specific collection after establishing a DB connection.
    If the connection fails, logs an error and exits.
    """
    db = get_db_connection()
    if db is None:
        logger.error("Database connection failed. Exiting...")
        exit(1)

    return db[collection_name]