'''
database_checks.py file is as follows:

    Purpose: This script contains functions to check and validate database tasks.
    Created Date: 2025-03-01
    Created By:  T.S.Balasooriya (tharindutsb@gmail.com) , Pasan(pasanbathiya246@gmail.com),Amupama(anupamamaheepala999@gmail.com)
    Last Modified Date: 2025-03-15
    Modified By: T.S.Balasooriya (tharindutsb@gmail.com), Pasan(pasanbathiya246@gmail.com),Amupama(anupamamaheepala999@gmail.com)     
    Version: Python 3.9
    Dependencies: datetime, utils.loggers, utils.Custom_Exceptions
    Notes:
'''

from datetime import datetime
from utils.loggers import get_logger
from utils.Custom_Exceptions import TaskValidationError

logger = get_logger("amend_status_logger")

def update_task_status(system_task_collection, task_id, status, error_description=None):
    """
    Updates the status of a task in the system_task collection.
    Also updates status_changed_dtm and status_description (if provided).
    Returns: (success, error)
    """
    try:
        logger.info(f"Updating task status to '{status}' for Task ID {task_id}...")
        
        # Prepare the update fields
        update_fields = {
            "task_status": status,
            "status_changed_dtm": datetime.now(),
            "last_updated": datetime.now()
        }
        
        # Add status_description if an error description is provided
        if error_description:
            update_fields["status_description"] = error_description
        
        # Update the task status and related fields
        system_task_collection.update_one(
            {"Task_Id": task_id},
            {"$set": update_fields}
        )
        
        logger.info(f"Task ID {task_id} status updated to '{status}' successfully.")
        return True, None
    except Exception as update_error:
        logger.error(f"Failed to update task status for Task ID {task_id}: {update_error}")
        raise TaskValidationError(f"Failed to update task status for Task ID {task_id}: {update_error}")

def fetch_and_validate_template_task(template_task_collection, template_task_id, task_type):
    """
    Fetches and validates the template task from the template_task collection.
    Returns: (success, template_task or error)
    """
    try:
        logger.info("Querying template_task collection for matching task...")
        template_task = template_task_collection.find_one({
            "Template_Task_Id": template_task_id,
            "task_type": task_type
        })
        if not template_task:
            error_message = f"No matching template task found for Template_Task_Id {template_task_id}."
            logger.error(error_message)
            return False, error_message
        return True, template_task
    except Exception as fetch_error:
        logger.error(f"Failed to fetch or validate template task: {fetch_error}")
        raise TaskValidationError(f"Failed to fetch or validate template task: {fetch_error}")

def fetch_transaction_details(transaction_collection, case_distribution_batch_id):
    """
    Fetches transaction details for the given batch ID.
    Returns: (success, amend_action or error)
    """
    try:
        logger.info(f"Querying transaction collection for Batch ID: {case_distribution_batch_id}...")
        transaction_record = transaction_collection.find_one({
            "Case_Distribution_Batch_ID": case_distribution_batch_id,
            "summery_status": "open",
            "batch_seq_details.CRD_Distribution_Status":"open"
        })
        if not transaction_record:
            error_message = f"No open transaction record found for Batch ID {case_distribution_batch_id}."
            logger.error(error_message)
            return False, error_message

        # Find the amend action in batch_seq_details
        amend_action = None
        for batch_seq in transaction_record.get("batch_seq_details", []):
            if batch_seq.get("action_type") == "amend" and batch_seq.get("CRD_Distribution_Status") == "open":
                amend_action = batch_seq
                break

        if not amend_action:
            error_message = f"No open amend action found for Batch ID {case_distribution_batch_id}."
            logger.error(error_message)
            return False, error_message

        # Validate array_of_distributions
        array_of_distributions = amend_action.get("array_of_distributions", [])
        if not array_of_distributions:
            error_message = f"No array_of_distributions found for amend action in Batch ID {case_distribution_batch_id}."
            logger.error(error_message)
            return False, error_message

        for distribution in array_of_distributions:
            if not all(key in distribution for key in ["rtom", "donor_drc_id", "receiver_drc_id", "transfer_count"]):
                error_message = f"Missing mandatory fields in array_of_distributions for Batch ID {case_distribution_batch_id}."
                logger.error(error_message)
                return False, error_message

        return True, amend_action
    except Exception as fetch_error:
        logger.error(f"Failed to fetch or validate transaction details: {fetch_error}")
        raise TaskValidationError(f"Failed to fetch or validate transaction details: {fetch_error}")

def fetch_cases_for_batch(case_collection, case_distribution_batch_id):
    """
    Fetches cases for the given batch ID from the case collection.
    Returns: (success, cases or error)
    """
    try:
        logger.info(f"Fetching cases for Batch ID {case_distribution_batch_id}...")
        cases = list(case_collection.find({"Case_Distribution_Batch_ID": case_distribution_batch_id}))
        logger.info(f"Found {len(cases)} cases for Batch ID {case_distribution_batch_id}.")
        return True, cases
    except Exception as fetch_error:
        logger.error(f"Failed to fetch cases for batch ID {case_distribution_batch_id}: {fetch_error}")
        raise TaskValidationError(f"Failed to fetch cases for batch ID {case_distribution_batch_id}: {fetch_error}")