'''
database_update.py file is as follows:

    Purpose: This script resets and imports data into MongoDB collections from JSON files.
    Created Date: 2025-01-08
    Created By:  T.S.Balasooriya (tharindutsb@gmail.com) , Pasan(pasanbathiya246@gmail.com),Amupama(anupamamaheepala999@gmail.com)
    Last Modified Date: 2024-01-19
    Modified By: T.S.Balasooriya (tharindutsb@gmail.com), Pasan(pasanbathiya246@gmail.com),Amupama(anupamamaheepala999@gmail.com)     
    Version: Python 3.9
    Dependencies: pymongo, json, os, bson
    Notes:
'''

import pymongo
import json
import os
from bson import ObjectId

# MongoDB connection details
client = pymongo.MongoClient('mongodb+srv://tharindutsb:tharindu2000@clusterdrc.7kyna.mongodb.net/?retryWrites=true&w=majority&appName=ClusterDRC')
db = client['drs_case_distribution_db']

# List of collections to reset
collections = [
    'Case_distribution_drc_transactions',
    'DRS_Database.Case_Distribution_DRC_Summary',
    'DRS.Tmp_Case_Distribution_DRC',
    'System_tasks',
    'Template_task'
]

# Directory containing JSON files
json_dir = r'Database json files'

# List of corresponding JSON file names
json_files = [
    os.path.join(json_dir, 'Case_distribution_drc_transactions.json'),
    os.path.join(json_dir, 'DRS_Database.Case_Distribution_DRC_Summary.json'),
    os.path.join(json_dir, 'DRS.Tmp_Case_Distribution_DRC.json'),
    os.path.join(json_dir, 'System_tasks.json'),
    os.path.join(json_dir, 'Template_task.json')
]

# Function to reset collections and insert data from JSON files
def reset_and_import_data():
    for collection_name, json_file in zip(collections, json_files):
        # Delete all documents from the collection
        collection = db[collection_name]
        collection.delete_many({})

        # Load data from the JSON file
        with open(json_file, 'r') as file:
            data = json.load(file)

        # Convert $oid fields to ObjectId
        def convert_oid(document):
            if isinstance(document, dict):
                for key, value in document.items():
                    if key == "_id" and "$oid" in value:
                        document[key] = ObjectId(value["$oid"])
                    else:
                        convert_oid(value)
            elif isinstance(document, list):
                for item in document:
                    convert_oid(item)

        convert_oid(data)

        # Insert data into the collection
        if isinstance(data, list):  # Assuming data is a list of documents
            collection.insert_many(data)
        else:  # If data is a single document
            collection.insert_one(data)
        print(f"Data imported into {collection_name} from {json_file}")

# Run the function
reset_and_import_data()
