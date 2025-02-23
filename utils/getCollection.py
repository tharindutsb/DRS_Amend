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