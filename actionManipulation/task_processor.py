from logger.loggers import get_logger
from actionManipulation.database_checks import update_task_status, fetch_and_validate_template_task, fetch_transaction_details, fetch_cases_for_batch
from actionManipulation.balance_resources import balance_resources
from actionManipulation.update_databases import update_case_distribution_collection, update_summary_in_mongo
from utils.connectDB import get_initialized_collections

# Initialize logger
logger = get_logger("task_processor_logger")

# Track active DRCs being processed
active_amendments = set()

def process_single_batch(task, case_collection, transaction_collection, summary_collection, system_task_collection, template_task_collection):
    """
    Processes a single batch for the given task.
    """
    task_id = task["Task_Id"]
    template_task_id = task["Template_Task_Id"]
    task_type = task["task_type"]
    case_distribution_batch_id = task["parameters"]["Case_Distribution_Batch_ID"]

    try:
        # Step 1: Update task status to "processing"
        update_task_status(system_task_collection, task_id, "processing")

        # Step 2: Fetch and validate template task
        template_task = fetch_and_validate_template_task(template_task_collection, template_task_id, task_type)

        # Step 3: Fetch transaction details
        amend_details = fetch_transaction_details(transaction_collection, case_distribution_batch_id)

        # Step 4: Fetch cases for the batch
        cases = fetch_cases_for_batch(case_collection, case_distribution_batch_id)

        # Convert cases to a dictionary format for balancing logic
        drcs = {} 
        existing_drcs = {}
        for case in cases:
            if "Case_Id" in case and "DRC_Id" in case and "RTOM" in case:
                drcs[case["Case_Id"]] = [case["DRC_Id"], case["RTOM"]]
                existing_drcs[case["Case_Id"]] = case["DRC_Id"]
            else:
                logger.error(f"Skipping case due to missing fields: {case}")

        # Step 5: Process amendments
        array_of_distributions = amend_details.get("array_of_distributions", [])
        for distribution in array_of_distributions:
            receiver_drc = distribution.get("receiver_drc_id")
            donor_drc = distribution.get("donor_drc_id")
            rtom = distribution.get("rtom")
            transfer_value = distribution.get("transfer_count")

            # Check for parallel access attempts
            if receiver_drc in active_amendments or donor_drc in active_amendments:
                logger.error(f"Parallel task detected: DRCs {receiver_drc} and/or {donor_drc} are already being processed. Skipping distribution.")
                continue

            # Mark DRCs as active
            active_amendments.add(receiver_drc)
            active_amendments.add(donor_drc)

            try:
                # Step 6: Run the balancing logic
                updated_drcs, amend_description = balance_resources(drcs, receiver_drc, donor_drc, rtom, transfer_value)

                # Step 7: Update case distribution collection
                update_case_distribution_collection(case_collection, updated_drcs, existing_drcs)

                # Step 8: Update summary in MongoDB
                update_summary_in_mongo(summary_collection, transaction_collection, updated_drcs, case_distribution_batch_id)

            finally:
                # Ensure DRCs are always removed from active set
                active_amendments.discard(receiver_drc)
                active_amendments.discard(donor_drc)

        # Step 9: Update task status to "completed"
        update_task_status(system_task_collection, task_id, "completed")
        logger.info(f"Task ID {task_id} completed successfully.")

    except Exception as e:
        logger.error(f"Error in Task ID {task_id}: {e}")
        update_task_status(system_task_collection, task_id, "failed")

def process_tasks(case_collection, transaction_collection, summary_collection, system_task_collection, template_task_collection):
    """
    Processes open tasks in system_tasks that match the template_task collection.
    """
    try:
        logger.info("Querying system_tasks collection for open tasks...")
        open_tasks = list(system_task_collection.find({
            "task_status": "open",
            "task_type": "Case Amend Planning among DRC"
        }))
        logger.info(f"Found {len(open_tasks)} open tasks.")

        # Process tasks sequentially
        for task in open_tasks:
            process_single_batch(
                task,
                case_collection,
                transaction_collection,
                summary_collection,
                system_task_collection,
                template_task_collection
            )

    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")
        
def amend_task_processing():
    """
    Initializes database collections and runs task processing.
    """
    logger.info("Initializing database collections for task processing...")

    # Get collections from MongoDB
    collections = get_initialized_collections()

    # Run task processing
    process_tasks(
        collections["case_collection"],
        collections["transaction_collection"],
        collections["summary_collection"],
        collections["system_task_collection"],
        collections["template_task_collection"]
    )