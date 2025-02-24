from openApi.services.get_amend_plan import get_amend_plan
from openApi.services.balance_resources import balance_resources
from openApi.services.update_amend_drcs import update_drcs_in_mongo
from openApi.models.amend_model import TaskStatus
from logger.loggers import get_logger
from utils.connectDB import get_db_connection

logger = get_logger(__name__)


def amend_resources(amend_request):
    """
    Handles the amendment request by fetching data from MongoDB, balancing resources, and updating MongoDB.
    
    :param amend_request: The amendment request containing rtom, donor_drc_id, receiver_drc_id, and transfer_count.
    :return: Updated DRCs with case IDs after balancing.
    :raises: Exception with detailed error message if any step fails
    """
    db = None
    try:
        # Get database connection
        db = get_db_connection()
        if db is None:
            logger.error("Failed to connect to database")
            raise Exception("Database connection failed")


        logger.info("Starting amendment process")

        
        # Access transactions collection
        collection = db["case_distribution_drc_transactions"]

        # Update task status to in-progress
        collection.update_one(
            {"case_distribution_batch_id": amend_request.case_distribution_batch_id},
            {"$set": {"batch_seq_details.$[elem].task_status": TaskStatus.IN_PROGRESS}},
            array_filters=[{"elem.batch_seq": amend_request.batch_seq_details[0].batch_seq}]
        )
        logger.info(f"Updated task status to IN_PROGRESS for batch {amend_request.batch_seq_details[0].batch_seq}")

        # Fetch data from MongoDB and get the amendment plan
        drcs, receiver_drc, donor_drc, rtom, transfer_value = get_amend_plan()
        logger.debug(f"Retrieved amendment plan: {receiver_drc}, {donor_drc}, {rtom}, {transfer_value}")


        # Perform the balance operation
        updated_drcs = balance_resources(drcs, receiver_drc, donor_drc, rtom, transfer_value)
        logger.info("Successfully balanced resources")

        # Update task status to completed
        collection.update_one(
            {"case_distribution_batch_id": amend_request.case_distribution_batch_id},
            {"$set": {"batch_seq_details.$[elem].task_status": TaskStatus.COMPLETED}},
            array_filters=[{"elem.batch_seq": amend_request.batch_seq_details[0].batch_seq}]
        )
        logger.info(f"Updated task status to COMPLETED for batch {amend_request.batch_seq_details[0].batch_seq}")

        return updated_drcs

        
    except Exception as e:
        logger.error(f"Error in amend_resources: {str(e)}", exc_info=True)
        if db:
            try:
                # Update task status to failed if error occurs
                collection = db["case_distribution_drc_transactions"]
                collection.update_one(
                    {"case_distribution_batch_id": amend_request.case_distribution_batch_id},
                    {"$set": {"batch_seq_details.$[elem].task_status": "failed"}},
                    array_filters=[{"elem.batch_seq": amend_request.batch_seq_details[0].batch_seq}]
                )
                logger.info(f"Updated task status to FAILED for batch {amend_request.batch_seq_details[0].batch_seq}")
            except Exception as status_error:
                logger.error(f"Failed to update task status to FAILED: {str(status_error)}")
        raise Exception(f"Amendment process failed: {str(e)}") from e
