from utils.connectDB import get_db_connection

def update_drcs_in_mongo(updated_drcs, amend_status, amend_description):
    """
    Updates only the changed DRCs in MongoDB with the new DRC IDs and amend details.
    
    :param updated_drcs: Dictionary of case IDs mapping to new DRC and resource pairs.
    :param amend_status: Status of the amendment ("Successful" or "Failed").
    :param amend_description: Description of the amendment (success details or error message).
    """
    try:
        # Get the database connection
        db = get_db_connection()
        if not db:
            raise Exception("Failed to connect to the database.")

        # Access the case_distribution_drc collection
        collection = db["case_distribution_drc"]

        # Fetch existing DRCs to compare with updated ones
        existing_drcs = {doc["Case_Id"]: doc["DRC_Id"] for doc in collection.find({}, {"Case_Id": 1, "DRC_Id": 1})}

        for case_id, (new_drc, _) in updated_drcs.items():
            # Check if DRC has changed
            if case_id in existing_drcs and existing_drcs[case_id] != new_drc:
                collection.update_one(
                    {"Case_Id": case_id},  # Find the document by Case_Id
                    {
                        "$set": {
                            "NEW_DRC_ID": new_drc,  # Update the NEW_DRC_ID only if changed
                            "Proceed_On": None,  # Set the current timestamp
                            "Amend_Status": amend_status,  # Set the Amend_Status
                            "Amend_Description": amend_description  # Set the Amend_Description
                        }
                    }
                )
                print(f"Updated Case ID {case_id}: NEW_DRC_ID -> {new_drc}")
            else:
                print(f"Skipped Case ID {case_id}: No change in DRC.")
    except Exception as e:
        print(f"Error updating DRCs in MongoDB: {e}")
        raise e