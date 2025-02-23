from utils.connectDB import get_db_connection
from logger.loggers import get_logger
import pymongo

logger = get_logger(__name__)



def get_amend_plan():
    """
    Retrieves the amendment plan from MongoDB.
    
    :return: A tuple containing:
             - drcs: Dictionary of case IDs mapping to DRC and resource pairs.
             - receiver_drc: The DRC receiving resources.
             - donor_drc: The DRC donating resources.
             - rtom: The resource to modify.
             - transfer_value: The value to transfer between resources.
    :raises: Exception with detailed error message if any step fails
    """
    try:
        logger.info("Retrieving amendment plan from MongoDB")
        
        # Get the database connection
        db = get_db_connection()
        if db is None or not isinstance(db, pymongo.database.Database):


            error_msg = "Failed to establish valid database connection"
            logger.error(error_msg)
            raise ConnectionError(error_msg)



        # Access the case_distribution_drc_transactions collection
        try:
            collection = db["case_distribution_drc_transactions"]
            if not isinstance(collection, pymongo.collection.Collection):
                raise ValueError("Invalid collection type")
            logger.debug("Successfully accessed case_distribution_drc_transactions collection")
        except Exception as e:
            error_msg = f"Failed to access collection: {str(e)}"
            logger.error(error_msg)
            raise ConnectionError(error_msg)


        # Fetch the latest amendment plan
        try:
            transaction_record = collection.find_one(sort=[("batch_seq_details.batch_seq", -1)])
            if not transaction_record:
                error_msg = "No transaction records found in collection"
                logger.warning(error_msg)
                raise ValueError(error_msg)
            logger.debug(f"Found transaction record with ID: {transaction_record.get('_id')}")
        except Exception as e:
            error_msg = f"Error fetching transaction record: {str(e)}"
            logger.error(error_msg)
            raise ConnectionError(error_msg)


            for batch_seq_detail in transaction_record.get("batch_seq_details", []):
                if batch_seq_detail.get("action_type") == "amend":
                    logger.debug("Found amend action in batch sequence details")
                    for distribution in batch_seq_detail.get("array_of_distributions", []):
                        logger.info("Successfully retrieved amendment plan")
                        return (
                            {},  # Placeholder for drcs (fetch from case_distribution_drc collection)
                            distribution.get("receiver_drc_id"),
                            distribution.get("donor_drc_id"),
                            distribution.get("rtom"),
                            distribution.get("transfer_count")
                        )
        
        error_msg = "No valid amendment plan found in database"
        logger.warning(error_msg)
        return None, None, None, None, None
        
    except Exception as e:
        logger.error(f"Error retrieving amendment plan: {str(e)}", exc_info=True)
        raise Exception(f"Failed to retrieve amendment plan: {str(e)}") from e
