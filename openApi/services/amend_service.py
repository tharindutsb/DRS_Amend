from openApi.services.get_amend_plan import get_amend_plan
from openApi.services.balance_resources import balance_resources
from logger.loggers import get_logger

logger = get_logger(__name__)

def amend_resources(amend_request):
    """
    Handles the amendment request by fetching data from MongoDB, balancing resources, and updating MongoDB.
    
    :param amend_request: The amendment request containing rtom, donor_drc_id, receiver_drc_id, and transfer_count.
    :return: Updated DRCs with case IDs after balancing.
    :raises: Exception with detailed error message if any step fails
    """
    try:
        logger.info("Starting amendment process")
        
        # Fetch data from MongoDB and get the amendment plan
        drcs, receiver_drc, donor_drc, rtom, transfer_value = get_amend_plan()
        logger.debug(f"Retrieved amendment plan: {receiver_drc}, {donor_drc}, {rtom}, {transfer_value}")

        # Perform the balance operation
        updated_drcs = balance_resources(drcs, receiver_drc, donor_drc, rtom, transfer_value)
        logger.info("Successfully balanced resources")

        return updated_drcs
        
    except Exception as e:
        logger.error(f"Error in amend_resources: {str(e)}", exc_info=True)
        raise Exception(f"Amendment process failed: {str(e)}") from e
