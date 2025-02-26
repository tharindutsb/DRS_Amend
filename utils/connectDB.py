import configparser
from pymongo import MongoClient
import os

def get_db_connection():
    config_path = os.path.join(os.path.dirname(__file__), "../Config/DB_Config.ini")

    # Check if configuration file exists
    if not os.path.exists(config_path):
        print(f"Configuration file '{config_path}' not found.")
        return None

    # Read the configuration file
    config = configparser.ConfigParser()
    config.read(config_path)

    # Ensure 'DATABASE' section exists
    if 'DATABASE' not in config:
        print("'DATABASE' section not found in DB_Config.ini")
        return None

    # Retrieve values
    mongo_uri = config['DATABASE'].get('MONGO_URI', '').strip()
    db_name = config['DATABASE'].get('DB_NAME', '').strip()

    if not mongo_uri or not db_name:
        print("Missing MONGO_URI or DB_NAME in DB_Config.ini")
        return None

    try:
        # Connect to MongoDB
        client = MongoClient(mongo_uri)
        db = client[db_name]
        # print(f"Connected to MongoDB successfully | dataBase name:{db_name}")
        return db
    except Exception as e:
        print(f"Error connecting to MongoDB: {e}")
        return None
    

# Initialize collections
def initialize_collections(db):
    """
    Initializes the collections using the database connection.
    
    Args:
        db: MongoDB database object.
    
    Returns:
        dict: A dictionary of collections.
    """
    # Collection names
    CASE_COLLECTION = "DRS.Tmp_Case_Distribution_DRC"
    TRANSACTION_COLLECTION = "Case_distribution_drc_transactions"
    CASE_DRC_SUMMARY = "DRS_Database.Case_Distribution_DRC_Summary"
    SYSTEM_TASK = "System_tasks"
    TEMPLATE_TASK = "Template_task"

    # Initialize collections
    collections = {
        "case_collection": db[CASE_COLLECTION],
        "transaction_collection": db[TRANSACTION_COLLECTION],
        "summary_collection": db[CASE_DRC_SUMMARY],
        "system_task_collection": db[SYSTEM_TASK],
        "template_task_collection": db[TEMPLATE_TASK],
    }
    return collections

if __name__ == "__main__":
    db_connection = get_db_connection()
    if db_connection is not None:
        print("Database connection established.")
    else:
        print("Database connection failed.")
