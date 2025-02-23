from utils.connectDB import get_db_connection

def get_amend_plan():
    """
    Retrieves the amendment plan from MongoDB.
    
    :return: A tuple containing:
             - drcs: Dictionary of case IDs mapping to DRC and resource pairs.
             - receiver_drc: The DRC receiving resources.
             - donor_drc: The DRC donating resources.
             - rtom: The resource to modify.
             - transfer_value: The value to transfer between resources.
    """
    try:
        # Get the database connection
        db = get_db_connection()
        if not db:
            raise Exception("Failed to connect to the database.")

        # Access the case_distribution_drc_transactions collection
        collection = db["case_distribution_drc_transactions"]

        # Fetch the latest amendment plan
        transaction_record = collection.find_one(sort=[("batch_seq_details.batch_seq", -1)])
        if transaction_record:
            for batch_seq_detail in transaction_record.get("batch_seq_details", []):
                if batch_seq_detail.get("action_type") == "amend":
                    for distribution in batch_seq_detail.get("array_of_distributions", []):
                        return (
                            {},  # Placeholder for drcs (fetch from case_distribution_drc collection)
                            distribution.get("receiver_drc_id"),
                            distribution.get("donor_drc_id"),
                            distribution.get("rtom"),
                            distribution.get("transfer_count")
                        )
        return None, None, None, None, None
    except Exception as e:
        raise e