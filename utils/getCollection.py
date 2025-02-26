import configparser
import os

def get_collection_name(collection_key):
    """
    Retrieves the collection name from the DB_Config.ini file based on the provided key.
    
    Args:
        collection_key (str): The key for the collection name in the INI file.
    
    Returns:
        str: The collection name corresponding to the key, or the key itself if not found.
    """
    # Construct the path to the DB_Config.ini file
    config_path = os.path.join(os.path.dirname(__file__), "../Config/DB_Config.ini")

    # Read the configuration file
    config = configparser.ConfigParser()
    config.read(config_path)

    # Retrieve the collection name from the 'COLLECTIONS' section
    return config['COLLECTIONS'].get(collection_key, collection_key)

# Test fetching the collection names
if __name__ == "__main__":
    print("Case Collection:", get_collection_name("CASE_COLLECTION"))
    print("Transaction Collection:", get_collection_name("TRANSACTION_COLLECTION"))
    print("Case DRC Summary:", get_collection_name("CASE_DRC_SUMMARY"))
    print("System Tasks:", get_collection_name("SYSTEM_TASKS"))
    print("Template Task:", get_collection_name("TEMPLATE_TASK"))