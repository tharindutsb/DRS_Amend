import configparser
import os
from utils.connectDB import get_db_connection

# Construct the path to the DB_Config.ini file
config_path = os.path.join(os.path.dirname(__file__), "../Config/DB_Config.ini")

# Initialize ConfigParser
config = configparser.ConfigParser()

# Read the configuration file
config.read(config_path)

# Collection names
CASE_COLLECTION = config['COLLECTIONS'].get('CASE_COLLECTION')
TRANSACTION_COLLECTION = config['COLLECTIONS'].get('TRANSACTION_COLLECTION')
CASE_DRC_SUMMARY = config['COLLECTIONS'].get('CASE_DRC_SUMMARY')
SYSTEM_TASK = config['COLLECTIONS'].get('SYSTEM_TASKS')
TEMPLATE_TASK = config['COLLECTIONS'].get('TEMPLATE_TASK')

# Establish database connection
db = get_db_connection()
if db is None:
    raise RuntimeError("Failed to connect to the database.")




# Test the database connection
if __name__ == "__main__":
    db_connection = get_db_connection()
    if db_connection is not None:
        print("Database connection established.")
    else:
        print("Database connection failed.")