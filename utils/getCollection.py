import configparser
import os

def get_collection_name(collection_key):
    config_path = os.path.join(os.path.dirname(__file__), "../Config/DB_Config.ini")

    config = configparser.ConfigParser()
    config.read(config_path)
    return config['COLLECTIONS'].get(collection_key, collection_key)

# Test fetching the collection names
print("Case Collection:", get_collection_name("CASE_COLLECTION"))
print("Transaction Collection:", get_collection_name("TRANSACTION_COLLECTION"))
print("Case DRC Summery",get_collection_name("CASE_DRC_SUMMERY"))
print("System Tasks",get_collection_name("SYSTEM_TASKS"))
print("Template Task",get_collection_name("TEMPLATE_TASK"))
