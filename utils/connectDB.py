'''
connectDB.py file is as follows:

    Purpose: This script handles database connections and collection initialization.
    Created Date: 2025-03-01
    Created By:  T.S.Balasooriya (tharindutsb@gmail.com) , Pasan(pasanbathiya246@gmail.com),Amupama(anupamamaheepala999@gmail.com)
    Last Modified Date: 2025-03-15
    Modified By: T.S.Balasooriya (tharindutsb@gmail.com), Pasan(pasanbathiya246@gmail.com),Amupama(anupamamaheepala999@gmail.com)     
    Version: Python 3.9
    Dependencies: configparser, pymongo, os, utils.loggers, utils.Custom_Exceptions
    Notes:
'''

import configparser
from pymongo import MongoClient
import os
from utils.loggers import get_logger
from utils.Custom_Exceptions import DatabaseConnectionError
from utils.filePath import get_filePath

# Collection names
CASE_COLLECTION = "DRS.Tmp_Case_Distribution_DRC"   # Temporary collection for case distribution
TRANSACTION_COLLECTION = "Case_distribution_drc_transactions"  # Collection for transactions related to Amend distribution
CASE_DRC_SUMMARY = "DRS_Database.Case_Distribution_DRC_Summary" # Collection for case distribution summary after amendment
SYSTEM_TASKS = "System_tasks"  # Collection for system tasks
TEMPLATE_TASK = "Template_task" # Collection for template task 

# Initialize logger
logger = get_logger("database_logger")

# Read configuration from DB_Config.ini file
def get_db_connection():

    config_path = get_filePath("DB_Config")
    if not os.path.exists(config_path):
        logger.error(f"Configuration file '{config_path}' not found.")
        raise DatabaseConnectionError(f"Configuration file '{config_path}' not found.")

    config = configparser.ConfigParser()
    config.read(config_path)

    if 'DATABASE' not in config:
        logger.error("'DATABASE' section not found in DB_Config.ini")
        raise DatabaseConnectionError("'DATABASE' section not found in DB_Config.ini")

    mongo_uri = config['DATABASE'].get('MONGO_URI', '').strip()
    db_name = config['DATABASE'].get('DB_NAME', '').strip()

    if not mongo_uri or not db_name:
        logger.error("Missing MONGO_URI or DB_NAME in DB_Config.ini")
        raise DatabaseConnectionError("Missing MONGO_URI or DB_NAME in DB_Config.ini")

    try:
        client = MongoClient(mongo_uri)
        db = client[db_name]
        return db
    except Exception as db_connection_error:
        logger.error(f"Error connecting to MongoDB: {db_connection_error}")
        raise DatabaseConnectionError(f"Error connecting to MongoDB: {db_connection_error}")

# Get a specific collection
def get_collection(collection_name):
    """
    Returns a specific collection after establishing a DB connection.
    If the connection fails, logs an error and exits.
    """
    db = get_db_connection()
    if db is None:
        logger.error("Database connection failed. Exiting...")
        raise DatabaseConnectionError("Database connection failed. Exiting...")

    return db[collection_name]