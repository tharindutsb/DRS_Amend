from datetime import datetime
from utils.loggers import get_logger

logger = get_logger("amend_status_logger")

def update_task_status(system_task_collection, task_id, status):
    """
    Updates the status of a task in the system_task collection.
    """
    try:
        logger.info(f"Updating task status to '{status}' for Task ID {task_id}...")
        system_task_collection.update_one(
            {"Task_Id": task_id},
            {"$set": {"task_status": status, "last_updated": datetime.now()}}
        )
        logger.info(f"Task ID {task_id} status updated to '{status}' successfully.")
    except Exception as e:
        logger.error(f"Failed to update task status for Task ID {task_id}: {e}")
        raise

def fetch_and_validate_template_task(template_task_collection, template_task_id, task_type):
    """
    Fetches and validates the template task from the template_task collection.
    Raises an exception if no matching template task is found.
    """
    try:
        logger.info("Querying template_task collection for matching task...")
        template_task = template_task_collection.find_one({
            "Template_Task_Id": template_task_id,
            "task_type": task_type
        })
        if not template_task:
            raise ValueError(f"No matching template task found for Template_Task_Id {template_task_id}.")
        return template_task
    except Exception as e:
        logger.error(f"Failed to fetch or validate template task: {e}")
        raise

def fetch_transaction_details(transaction_collection, case_distribution_batch_id):
    """
    Fetches transaction details for the given batch ID.
    Raises an exception if no transaction record is found or if mandatory fields are missing.
    """
    try:
        logger.info(f"Querying transaction collection for Batch ID: {case_distribution_batch_id}...")
        transaction_record = transaction_collection.find_one({
            "Case_Distribution_Batch_ID": case_distribution_batch_id,
            "summery_status": "open",
            "batch_seq_details.CRD_Distribution_Status": "open"
        })
        if not transaction_record:
            raise ValueError(f"No open transaction record found for Batch ID {case_distribution_batch_id}.")

        # Find the amend action in batch_seq_details
        amend_action = None
        for batch_seq in transaction_record.get("batch_seq_details", []):
            if batch_seq.get("action_type") == "amend" and batch_seq.get("CRD_Distribution_Status") == "open":
                amend_action = batch_seq
                break

        if not amend_action:
            raise ValueError(f"No open amend action found for Batch ID {case_distribution_batch_id}.")

        # Validate array_of_distributions
        array_of_distributions = amend_action.get("array_of_distributions", [])
        if not array_of_distributions:
            raise ValueError(f"No array_of_distributions found for amend action in Batch ID {case_distribution_batch_id}.")

        for distribution in array_of_distributions:
            if not all(key in distribution for key in ["rtom", "donor_drc_id", "receiver_drc_id", "transfer_count"]):
                raise ValueError(f"Missing mandatory fields in array_of_distributions for Batch ID {case_distribution_batch_id}.")

        return amend_action
    except Exception as e:
        logger.error(f"Failed to fetch or validate transaction details: {e}")
        raise

def fetch_cases_for_batch(case_collection, case_distribution_batch_id):
    """
    Fetches cases for the given batch ID from the case collection.
    """
    try:
        logger.info(f"Fetching cases for Batch ID {case_distribution_batch_id}...")
        cases = list(case_collection.find({"Case_Distribution_Batch_ID": case_distribution_batch_id}))
        logger.info(f"Found {len(cases)} cases for Batch ID {case_distribution_batch_id}.")
        return cases
    except Exception as e:
        logger.error(f"Failed to fetch cases for batch ID {case_distribution_batch_id}: {e}")
        raise