from utils.loggers import get_logger
from actionManipulation.database_checks import update_task_status, fetch_and_validate_template_task, fetch_transaction_details, fetch_cases_for_batch
from actionManipulation.balance_resources import balance_resources
from actionManipulation.update_databases import update_case_distribution_collection, update_summary_in_mongo, rollback_case_distribution_collection, rollback_summary_in_mongo
from utils.connectDB import get_collection

# Initialize logger
logger = get_logger("amend_status_logger")

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
        success, error = update_task_status(system_task_collection, task_id, "processing")
        if error:
            raise Exception(error)

        # Step 2: Fetch and validate template task
        template_task_collection = get_collection("Template_task")
        template_task, error = fetch_and_validate_template_task(template_task_collection, template_task_id, task_type)
        if error:
            raise Exception(error)

        # Step 3: Fetch transaction details
        transaction_collection = get_collection("Case_distribution_drc_transactions")
        amend_details, error = fetch_transaction_details(transaction_collection, case_distribution_batch_id)
        if error:
            raise Exception(error)

        # Step 4: Fetch cases for the batch
        case_collection = get_collection("DRS.Tmp_Case_Distribution_DRC")
        cases, error = fetch_cases_for_batch(case_collection, case_distribution_batch_id)
        if error:
            raise Exception(error)

        # Convert cases to a dictionary format for balancing logic
        drcs = {} 
        existing_drcs = {}
        for case in cases:
            if "Case_Id" in case and "DRC_Id" in case and "RTOM" in case:
                drcs[case["Case_Id"]] = [case["DRC_Id"], case["RTOM"]]
                existing_drcs[case["Case_Id"]] = case["DRC_Id"]
            else:
                logger.warning(f"Skipping case due to missing fields: {case}")

        # Step 5: Process amendments
        array_of_distributions = amend_details.get("array_of_distributions", [])
        for distribution in array_of_distributions:
            receiver_drc = distribution.get("receiver_drc_id")
            donor_drc = distribution.get("donor_drc_id")
            rtom = distribution.get("rtom")
            transfer_value = distribution.get("transfer_count")

            # Step 6: Run the balancing logic
            updated_drcs, error = balance_resources(drcs, receiver_drc, donor_drc, rtom, transfer_value)
            if error:
                raise Exception(error)

            # Step 7: Update case distribution collection
            success, error, original_states = update_case_distribution_collection(case_collection, updated_drcs, existing_drcs)
            if error:
                raise Exception(error)

            # Step 8: Update summary in MongoDB
            summary_collection = get_collection("DRS_Database.Case_Distribution_DRC_Summary")
            success, error, original_counts = update_summary_in_mongo(summary_collection, transaction_collection, updated_drcs, case_distribution_batch_id)
            if error:
                # Rollback case distribution collection if summary update fails
                rollback_case_distribution_collection(case_collection, original_states)
                raise Exception(error)

        # Step 9: Update task status to "completed"
        success, error = update_task_status(system_task_collection, task_id, "completed")
        if error:
            # Rollback both case distribution and summary collections if task status update fails
            rollback_case_distribution_collection(case_collection, original_states)
            rollback_summary_in_mongo(summary_collection, original_counts, case_distribution_batch_id)
            raise Exception(error)
        logger.info(f"Task ID {task_id} completed successfully.")

    except Exception as error_message:
        logger.error(f"Error in Task ID {task_id}: {error_message}")
        update_task_status(system_task_collection, task_id, "failed")

def amend_task_processing():
    """
    Processes all open tasks in the system.
    """
    logger.info("Starting task processing...")

    try:
        # Fetch all open tasks
        system_task_collection = get_collection("System_tasks")
        open_tasks = list(system_task_collection.find({
            "task_status": "open",
            "task_type": "Case Amend Planning among DRC"
        }))

        if not open_tasks:
            logger.info("No open tasks found.")
            return

        # Process each task
        for task in open_tasks:
            process_single_batch(task)

    except Exception as error_message:
        logger.error(f"An unexpected error occurred: {error_message}")
        
    logger.info("Task processing completed.")