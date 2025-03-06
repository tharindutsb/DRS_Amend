# import configparser
# from pymongo import MongoClient
# import os

# # collection names
# CASE_COLLECTION = "DRS.Tmp_Case_Distribution_DRC"
# TRANSACTION_COLLECTION = "Case_distribution_drc_transactions"
# CASE_DRC_SUMMARY = "DRS_Database.Case_Distribution_DRC_Summary"
# SYSTEM_TASKS = "System_tasks"
# TEMPLATE_TASK = "Template_task"


# def get_db_connection():
#     config_path = os.path.join(os.path.dirname(__file__), "../Config/DB_Config.ini")

#     # Check if configuration file exists
#     if not os.path.exists(config_path):
#         print(f"Configuration file '{config_path}' not found.")
#         return None

#     # Read the configuration file
#     config = configparser.ConfigParser()
#     config.read(config_path)

#     # Ensure 'DATABASE' section exists
#     if 'DATABASE' not in config:
#         print("'DATABASE' section not found in DB_Config.ini")
#         return None

#     # Retrieve values
#     mongo_uri = config['DATABASE'].get('MONGO_URI', '').strip()
#     db_name = config['DATABASE'].get('DB_NAME', '').strip()

#     if not mongo_uri or not db_name:
#         print("Missing MONGO_URI or DB_NAME in DB_Config.ini")
#         return None

#     try:
#         # Connect to MongoDB
#         client = MongoClient(mongo_uri)
#         db = client[db_name]
#         # print(f"Connected to MongoDB successfully | dataBase name:{db_name}")
#         return db
#     except Exception as e:
#         print(f"Error connecting to MongoDB: {e}")
#         return None
    

# # Initialize collections
# def initialize_collections(db):
#     """
#     Initializes the collections using the database connection.
    
#     Args:
#         db: MongoDB database object.
    
#     Returns:
#         dict: A dictionary of collections.
#     """

#     # Initialize collections
#     collections = {
#         "case_collection": db[CASE_COLLECTION],
#         "transaction_collection": db[TRANSACTION_COLLECTION],
#         "summary_collection": db[CASE_DRC_SUMMARY],
#         "system_task_collection": db[SYSTEM_TASKS],
#         "template_task_collection": db[TEMPLATE_TASK],
#     }
#     return collections

# if __name__ == "__main__":
#     db_connection = get_db_connection()
#     if db_connection is not None:
#         print("Database connection established.")
#     else:
#         print("Database connection failed.")



import configparser
from pymongo import MongoClient
import os
from logger.loggers import get_logger
from actionManipulationCopy.task_processor import process_tasks

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

def get_initialized_collections():
    """
    Returns initialized collections after establishing a DB connection.
    If the connection fails, logs an error and exits.
    """
    db = get_db_connection()
    if db is None:
        logger.error("Database connection failed. Exiting...")
        exit(1)

    collections = {
        "case_collection": db[CASE_COLLECTION],
        "transaction_collection": db[TRANSACTION_COLLECTION],
        "summary_collection": db[CASE_DRC_SUMMARY],
        "system_task_collection": db[SYSTEM_TASKS],
        "template_task_collection": db[TEMPLATE_TASK],
    }

    return collections

def run_task_processing():
    """
    Initializes database collections and runs task processing.
    """
    logger.info("Initializing database collections for task processing...")

    # Get collections from MongoDB
    collections = get_initialized_collections()

    # Run task processing
    process_tasks(
        collections["case_collection"],
        collections["transaction_collection"],
        collections["summary_collection"],
        collections["system_task_collection"],
        collections["template_task_collection"]
    )

    logger.info("Task processing completed.")
