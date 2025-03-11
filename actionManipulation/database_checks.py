from datetime import datetime
from utils.loggers import get_logger

logger = get_logger("amend_status_logger")

def update_task_status(system_task_collection, task_id, status):
    """
    Updates the status of a task in the system_task collection.
    Returns: (success, error)
    """
    try:
        logger.info(f"Updating task status to '{status}' for Task ID {task_id}...")
        system_task_collection.update_one(
            {"Task_Id": task_id},
            {"$set": {"task_status": status, "last_updated": datetime.now()}}
        )
        logger.info(f"Task ID {task_id} status updated to '{status}' successfully.")
        return True  # Success
    except Exception as error_message:
        logger.error(f"Failed to update task status for Task ID {task_id}: {error_message}")
        return False, str(error_message)  # Error

def fetch_and_validate_template_task(template_task_collection, template_task_id, task_type):
    """
    Fetches and validates the template task from the template_task collection.
    Returns: (template_task, error)
    """
    try:
        logger.info("Querying template_task collection for matching task...")
        template_task = template_task_collection.find_one({
            "Template_Task_Id": template_task_id,
            "task_type": task_type
        })
        if not template_task:
            logger.error(f"No matching template task found for Template_Task_Id {template_task_id}.")
            return False, f"No matching template task found for Template_Task_Id {template_task_id}."
        return True, template_task  # Success
    except Exception as error_message:
        logger.error(f"Failed to fetch or validate template task: {error_message}")
        return False, str(error_message)  # Error

def fetch_transaction_details(transaction_collection, case_distribution_batch_id):
    """
    Fetches transaction details for the given batch ID.
    Returns: (amend_action, error)
    """
    try:
        logger.info(f"Querying transaction collection for Batch ID: {case_distribution_batch_id}...")
        transaction_record = transaction_collection.find_one({
            "Case_Distribution_Batch_ID": case_distribution_batch_id,
            "summery_status": "open",
            "batch_seq_details.CRD_Distribution_Status": "open"
        })
        if not transaction_record:
            logger.error(f"No open transaction record found for Batch ID {case_distribution_batch_id}.")
            return False, f"No open transaction record found for Batch ID {case_distribution_batch_id}."

        # Find the amend action in batch_seq_details
        amend_action = None
        for batch_seq in transaction_record.get("batch_seq_details", []):
            if batch_seq.get("action_type") == "amend" and batch_seq.get("CRD_Distribution_Status") == "open":
                amend_action = batch_seq
                break

        if not amend_action:
            logger.error(f"No open amend action found for Batch ID {case_distribution_batch_id}.")
            return False, f"No open amend action found for Batch ID {case_distribution_batch_id}."

        # Validate array_of_distributions
        array_of_distributions = amend_action.get("array_of_distributions", [])
        if not array_of_distributions:
            logger.error(f"No array_of_distributions found for amend action in Batch ID {case_distribution_batch_id}.")
            return False, f"No array_of_distributions found for amend action in Batch ID {case_distribution_batch_id}."

        for distribution in array_of_distributions:
            if not all(key in distribution for key in ["rtom", "donor_drc_id", "receiver_drc_id", "transfer_count"]):
                logger.error(f"Missing mandatory fields in array_of_distributions for Batch ID {case_distribution_batch_id}.")
                return False, f"Missing mandatory fields in array_of_distributions for Batch ID {case_distribution_batch_id}."

        return True, amend_action  # Success
    except Exception as error_message:
        logger.error(f"Failed to fetch or validate transaction details: {error_message}")
        return False, str(error_message)  # Error

def fetch_cases_for_batch(case_collection, case_distribution_batch_id):
    """
    Fetches cases for the given batch ID from the case collection.
    Returns: (cases, error)
    """
    try:
        logger.info(f"Fetching cases for Batch ID {case_distribution_batch_id}...")
        cases = list(case_collection.find({"Case_Distribution_Batch_ID": case_distribution_batch_id}))
        logger.info(f"Found {len(cases)} cases for Batch ID {case_distribution_batch_id}.")
        return True, cases  # Success
    except Exception as error_message:
        logger.error(f"Failed to fetch cases for batch ID {case_distribution_batch_id}: {error_message}")
        return False, str(error_message)  # Error