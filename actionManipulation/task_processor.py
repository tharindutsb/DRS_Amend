'''
task_processor.py file is as follows:

    Purpose: This script processes tasks related to DRC Amend.
    Created Date: 2025-03-01
    Created By:  T.S.Balasooriya (tharindutsb@gmail.com) , Pasan(pasanbathiya246@gmail.com),Amupama(anupamamaheepala999@gmail.com)
    Last Modified Date: 2025-03-15
    Modified By: T.S.Balasooriya (tharindutsb@gmail.com), Pasan(pasanbathiya246@gmail.com),Amupama(anupamamaheepala999@gmail.com)     
    Version: Python 3.9
    Dependencies: utils.loggers, actionManipulation.database_checks, actionManipulation.balance_resources, actionManipulation.update_databases, utils.connectDB, utils.read_template_task_id_ini, datetime, utils.Custom_Exceptions
    Notes:
'''

from utils.loggers import get_logger
from actionManipulation.database_checks import update_task_status, fetch_and_validate_template_task, fetch_transaction_details, fetch_cases_for_batch
from actionManipulation.balance_resources import balance_resources
from actionManipulation.update_databases import update_case_distribution_collection, update_summary_in_mongo, rollback_case_distribution_collection, rollback_summary_in_mongo, update_template_task_collection
from utils.connectDB import get_collection
from utils.read_template_task_id_ini import get_template_task_id
from utils.Custom_Exceptions import TaskProcessingException

# Initialize logger
logger = get_logger("amend_status_logger")

def check_template_task_in_system_tasks(template_task_id):
    """
    Checks if the TEMPLATE_TASK_ID exists in the System_tasks collection.
    Returns: (success, exists or error)
    """
    try:
        system_task_collection = get_collection("System_tasks")
        
        # Check if the template_task_id exists in the System_tasks collection
        exists = system_task_collection.find_one({"Template_Task_Id": template_task_id}) is not None
        
        if exists:
            logger.info(f"Template_Task_Id {template_task_id} exists in the System_tasks collection.")
        else:
            logger.warning(f"Template_Task_Id {template_task_id} does not exist in the System_tasks collection.")
        
        return True, exists
    except Exception as db_check_error:
        logger.error(f"Failed to check System_tasks collection: {db_check_error}")
        return False, str(db_check_error)

def validate_template_task_parameters(system_task, template_task):
    """
    Validates that the Template_Task_Id, task_type, and parameters match between the System_tasks and Template_Task collections.
    Returns: (success, message or error)
    """
    try:
        if system_task["Template_Task_Id"] != template_task["Template_Task_Id"]:
            mismatch_template_task_id_error = f"Template_Task_Id mismatch: System_tasks has {system_task['Template_Task_Id']}, Template_Task has {template_task['Template_Task_Id']}."
            logger.error(mismatch_template_task_id_error)
            return False, mismatch_template_task_id_error

        if system_task["task_type"] != template_task["task_type"]:
            mismatch_task_type_error = f"Task type mismatch: System_tasks has {system_task['task_type']}, Template_Task has {template_task['task_type']}."
            logger.error(mismatch_task_type_error)
            return False, mismatch_task_type_error

        # Check parameters (e.g., Case_Distribution_Batch_ID)
        system_task_batch_id = system_task["parameters"].get("Case_Distribution_Batch_ID", "")
        template_task_batch_id = template_task["parameters"].get("Case_Distribution_Batch_ID", "")

        if system_task_batch_id != template_task_batch_id:
            mismatch_batch_id_error = f"Case_Distribution_Batch_ID mismatch: System_tasks has {system_task_batch_id}, Template_Task has {template_task_batch_id}."
            logger.error(mismatch_batch_id_error)
            return False, mismatch_batch_id_error

        logger.info("Template_Task_Id, task_type, and parameters match between System_tasks and Template_Task collections.")
        return True, "Parameters validated successfully."
    except Exception as validation_error:
        logger.error(f"Failed to validate template task parameters: {validation_error}")
        return False, str(validation_error)

def process_single_batch(task):
    """
    Processes a single batch for the given task.
    """
    task_id = task["Task_Id"]
    template_task_id = task["Template_Task_Id"]
    task_type = task["task_type"]
    case_distribution_batch_id = task["parameters"]["Case_Distribution_Batch_ID"]

    try:
        # Step 1: Update task status to "processing"
        system_task_collection = get_collection("System_tasks")
        success_update_task_status, error = update_task_status(system_task_collection, task_id, "processing", "Task is being processed")
        if not success_update_task_status:
            raise TaskProcessingException(error)

        # Step 2: Fetch and validate template task
        template_task_collection = get_collection("Template_task")
        success_fetch_template_task, template_task = fetch_and_validate_template_task(template_task_collection, template_task_id, task_type)
        if not success_fetch_template_task:
            raise TaskProcessingException(template_task)

        # Step 3: Validate that the Template_Task_Id, task_type, and parameters match between System_tasks and Template_Task collections
        success_validate_parameters, error = validate_template_task_parameters(task, template_task)
        if not success_validate_parameters:
            raise TaskProcessingException(error)

        # Step 4: Fetch transaction details
        transaction_collection = get_collection("Case_distribution_drc_transactions")
        success_fetch_transaction_details, amend_details = fetch_transaction_details(transaction_collection, case_distribution_batch_id)
        if not success_fetch_transaction_details:
            raise TaskProcessingException(amend_details)

        # Step 5: Fetch cases for the batch
        case_collection = get_collection("DRS.Tmp_Case_Distribution_DRC")
        success_fetch_cases_for_batch, cases = fetch_cases_for_batch(case_collection, case_distribution_batch_id)
        if not success_fetch_cases_for_batch:
            raise TaskProcessingException(cases)

        # Convert cases to a dictionary format for balancing logic
        drcs = {} 
        existing_drcs = {}
        for case in cases:
            if "Case_Id" in case and "DRC_Id" in case and "RTOM" in case:
                drcs[case["Case_Id"]] = [case["DRC_Id"], case["RTOM"]]
                existing_drcs[case["Case_Id"]] = case["DRC_Id"]
            else:
                logger.warning(f"Skipping case due to missing fields: {case}")

        # Step 6: Process amendments
        array_of_distributions = amend_details.get("array_of_distributions", [])
        for distribution in array_of_distributions:
            receiver_drc = distribution.get("receiver_drc_id")
            donor_drc = distribution.get("donor_drc_id")
            rtom = distribution.get("rtom")
            transfer_value = distribution.get("transfer_count")

            # Step 7: Run the balancing logic
            success_balance_resources, updated_drcs = balance_resources(drcs, receiver_drc, donor_drc, rtom, transfer_value)
            if not success_balance_resources:
                raise TaskProcessingException(updated_drcs)

            # Step 8: Update case distribution collection
            success_update_case_distribution, original_states = update_case_distribution_collection(case_collection, updated_drcs, existing_drcs)
            if not success_update_case_distribution:
                raise TaskProcessingException(original_states)

            # Step 9: Update summary in MongoDB
            summary_collection = get_collection("DRS_Database.Case_Distribution_DRC_Summary")
            success_update_summary, original_counts = update_summary_in_mongo(summary_collection, transaction_collection, updated_drcs, case_distribution_batch_id)
            if not success_update_summary:
                # Rollback case distribution collection if summary update fails
                rollback_case_distribution_collection(case_collection, original_states)
                raise TaskProcessingException(original_counts)

        # Step 10: Update task status to "completed"
        success_update_task_status_completed, error = update_task_status(system_task_collection, task_id, "completed", "Task completed successfully")
        if not success_update_task_status_completed:
            # Rollback both case distribution and summary collections if task status update fails
            rollback_case_distribution_collection(case_collection, original_states)
            rollback_summary_in_mongo(summary_collection, original_counts, case_distribution_batch_id)
            raise TaskProcessingException(error)
        logger.info(f"Task ID {task_id} completed successfully.")

    except TaskProcessingException as error_message:
        logger.error(f"Error in Task ID {task_id}: {error_message}")
        # Update task status to "error" and add error description
        update_task_status(system_task_collection, task_id, "error", str(error_message))

def amend_task_processing():
    """
    Processes all open tasks in the system.
    """
    logger.info("Starting task processing...")

    try:
        # Step 1: Read the TEMPLATE_TASK_ID from the INI file
        template_task_id = get_template_task_id()

        # Step 2: Update the Template_Task collection with the new TEMPLATE_TASK_ID and parameters
        system_task_collection = get_collection("System_tasks")
        open_tasks = list(system_task_collection.find({
            "task_status": "open",
            "task_type": "Case Amend Planning among DRC"
        }))

        if not open_tasks:
            logger.warning(f"No open tasks found for Template_Task_Id {template_task_id}. Skipping resource balancing.")
            return

        for task in open_tasks:
            case_distribution_batch_id = task["parameters"].get("Case_Distribution_Batch_ID", "")
            success_update_template_task, error = update_template_task_collection(case_distribution_batch_id)
            if not success_update_template_task:
                raise TaskProcessingException(error)

            # Step 3: Fetch the Template_Task record for validation
            template_task_collection = get_collection("Template_task")
            template_task = template_task_collection.find_one({
                "Template_Task_Id": template_task_id,
                "task_type": "Case Amend Planning among DRC"
            })

            if not template_task:
                error_message = f"No matching template task found for Template_Task_Id {template_task_id} and task_type 'Case Amend Planning among DRC'."
                logger.error(error_message)
                raise TaskProcessingException(error_message)

            # Step 4: Validate Template_Task_Id, task_type, and parameters
            success_validate_parameters, error = validate_template_task_parameters(task, template_task)
            if not success_validate_parameters:
                raise TaskProcessingException(error)

            # Step 5: Process the task
            process_single_batch(task)

    except TaskProcessingException as processing_error:
        logger.error(f"An unexpected error occurred during task processing: {processing_error}")
        
    logger.info("Task processing completed.")