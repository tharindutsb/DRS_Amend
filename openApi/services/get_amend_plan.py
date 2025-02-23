from utils.connectDB import get_db_connection

def get_amend_plan():
    """
    Retrieves DRC data from MongoDB and converts it into a dictionary format for use in balancing resources.
    
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

        # Access the case_distribution_drc collection
        collection_drc = db["case_distribution_drc"]

        # Query all records
        records_drc = collection_drc.find()

        # Convert the records to a format that can be passed to balance_resources
        drcs = {}
        for record in records_drc:
            case_id = record["Case_Id"]
            drc_id = record["DRC_Id"]
            rtom = record["RTOM"]
            drcs[case_id] = [drc_id, rtom]

        # Access the Case_distribution_drc_transactions collection
        collection_transactions = db["Case_distribution_drc_transactions"]

        # Fetch the latest transaction record
        transaction_record = collection_transactions.find_one()

        if transaction_record:
            for batch_seq_detail in transaction_record.get("batch_seq_details", []):
                if batch_seq_detail.get("action_type") == "amend":
                    for distribution in batch_seq_detail.get("array_of_distributions", []):
                        receiver_drc = distribution.get("receiver_drc_id")
                        donor_drc = distribution.get("donor_drc_id")
                        rtom = distribution.get("rtom")
                        transfer_value = distribution.get("transfer_count")
                        return drcs, receiver_drc, donor_drc, rtom, transfer_value

        # If no amend action is found, return the original drcs data
        return drcs, None, None, None, None
    except Exception as e:
        print(f"Error in get_amend_plan: {e}")
        raise e