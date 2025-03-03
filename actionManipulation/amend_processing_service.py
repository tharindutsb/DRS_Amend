from datetime import datetime
from collections import defaultdict
import threading
import logging
from logging.handlers import RotatingFileHandler
from utils.connectDB import get_db_connection, initialize_collections

# Logger Configuration
def get_logger(name):
    """
    Configures and returns a logger with the given name.
    Logs are written to both the console and a file.
    """
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    # File handler (writes logs to a file)
    file_handler = RotatingFileHandler(f"{name}.log", maxBytes=1024 * 1024, backupCount=5)
    file_handler.setLevel(logging.DEBUG)

    # Console handler (writes logs to the console)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)

    # Log format
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    # Add handlers to the logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger

# Initialize logger
logger = get_logger("name1")
logger.info("Logger initialized successfully.")

# Database connection and collections
db = get_db_connection()
if db is None:
    logger.error("Failed to connect to the database.")
    raise RuntimeError("Failed to connect to the database.")

collections = initialize_collections(db)
case_collection = collections["case_collection"]
transaction_collection = collections["transaction_collection"]
summary_collection = collections["summary_collection"]
system_task_collection = collections["system_task_collection"]
template_task_collection = collections["template_task_collection"]

# Locking mechanism for parallel processing
lock = threading.Lock()
active_amendments = set()  # Tracks DRCs currently being amended

def update_task_status(task_id, status):
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

def fetch_and_validate_template_task(template_task_id, task_type):
    """
    Fetches and validates the template task from the template_task collection.
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

def fetch_transaction_details(batch_id):
    """
    Fetches transaction details for the given batch ID.
    """
    try:
        logger.info(f"Querying transaction collection for Batch ID: {batch_id}...")
        transaction_record = transaction_collection.find_one({"Case_Distribution_Batch_ID": batch_id})
        if not transaction_record:
            raise ValueError(f"No transaction record found for Batch ID {batch_id}.")

        amend_details = next((seq for seq in transaction_record.get("batch_seq_details", []) if seq.get("action_type") == "amend"), None)
        if not amend_details or not amend_details.get("array_of_distributions"):
            raise ValueError(f"No amend action or array_of_distributions found for Batch ID {batch_id}.")

        return amend_details
    except Exception as e:
        logger.error(f"Failed to fetch or validate transaction details: {e}")
        raise

def fetch_cases_for_batch(batch_id):
    """
    Fetches cases for the given batch ID.
    """
    try:
        logger.info(f"Fetching cases for Batch ID {batch_id}...")
        cases = list(case_collection.find({"Case_Distribution_Batch_ID": batch_id}))
        logger.info(f"Found {len(cases)} cases for Batch ID {batch_id}.")
        return cases
    except Exception as e:
        logger.error(f"Failed to fetch cases for batch: {e}")
        raise

def balance_resources(drcs, receiver_drc, donor_drc, rtom, transfer_value):
    """
    Balances resources between DRCs.
    """
    resource_tracker = defaultdict(lambda: defaultdict(list))
    for case_id, (drc, resource) in drcs.items():
        resource_tracker[drc][resource].append(case_id)

    try:
        if receiver_drc not in resource_tracker or donor_drc not in resource_tracker:
            raise ValueError(f"One of the DRCs ({receiver_drc} or {donor_drc}) does not exist.")
        if rtom not in resource_tracker[receiver_drc] or rtom not in resource_tracker[donor_drc]:
            raise ValueError(f"The resource {rtom} does not exist in both {receiver_drc} and {donor_drc}.")

        donor_resource_count = len(resource_tracker[donor_drc][rtom])
        if donor_resource_count - transfer_value < 0.2 * donor_resource_count:
            raise ValueError(f"Insufficient resources in {donor_drc} for the Donate.")

        receiver_resource_count = len(resource_tracker[receiver_drc][rtom])
        if receiver_resource_count - transfer_value < 0.2 * receiver_resource_count:
            raise ValueError(f"Insufficient resources in {receiver_drc} for the Balance.")

        for _ in range(transfer_value):
            case_id = resource_tracker[donor_drc][rtom].pop(0)
            resource_tracker[receiver_drc][rtom].append(case_id)

        common_resources = set(resource_tracker[receiver_drc].keys()).intersection(set(resource_tracker[donor_drc].keys()))
        common_resources.discard(rtom)
        sorted_resources = sorted(common_resources, key=lambda x: len(resource_tracker[receiver_drc][x]), reverse=True)

        remaining_value = transfer_value
        index = 0
        while remaining_value > 0:
            resource = sorted_resources[index % len(sorted_resources)]
            if len(resource_tracker[receiver_drc][resource]) >= 1:
                case_id = resource_tracker[receiver_drc][resource].pop(0)
                resource_tracker[donor_drc][resource].append(case_id)
                remaining_value -= 1
            index += 1

        updated_drcs = {}
        for drc, resources in resource_tracker.items():
            for resource, case_ids in resources.items():
                for case_id in case_ids:
                    updated_drcs[case_id] = [drc, resource]
        return updated_drcs, f"Successfully transferred {transfer_value} cases of {rtom} from {donor_drc} to {receiver_drc}."
    except Exception as e:
        return drcs, str(e)

def update_case_distribution_collection(updated_drcs, existing_drcs):
    """
    Updates the case distribution collection with the new DRC and resource values.
    """
    try:
        logger.info("Updating case distribution collection...")
        for case_id, (new_drc, resource) in updated_drcs.items():
            if case_id in existing_drcs and existing_drcs[case_id] != new_drc:
                case_collection.update_one(
                    {"Case_Id": case_id},
                    {"$set": {"NEW_DRC_ID": new_drc, "Proceed_On": datetime.now(), "Amend_Status": "Completed", "Amend_Description": f"Transferred to {new_drc}"}}
                )
        logger.info("Case distribution collection updated successfully.")
    except Exception as e:
        logger.error(f"Failed to update case distribution collection: {e}")
        raise

def update_summary_in_mongo(updated_drcs, batch_id):
    """
    Updates the summary collection with the new counts after balancing.
    """
    try:
        logger.info("Updating summary collection...")
        count_dict = defaultdict(lambda: defaultdict(int))
        for case_id, (drc, rtom) in updated_drcs.items():
            count_dict[drc][rtom] += 1

        for drc, resources in count_dict.items():
            for rtom, count in resources.items():
                summary_collection.update_one(
                    {"Case_Distribution_Batch_ID": batch_id, "DRC_Id": drc, "RTOM": rtom},
                    {"$set": {"Count": count}},
                    upsert=True
                )
        logger.info("Summary collection updated successfully.")
    except Exception as e:
        logger.error(f"Failed to update summary collection: {e}")
        raise

def process_single_batch(task):
    """
    Processes a single batch for the given task.
    """
    task_id = task["Task_Id"]
    template_task_id = task["Template_Task_Id"]
    task_type = task["task_type"]
    batch_id = task["parameters"]["Case_Distribution_Batch_ID"]

    update_task_status(task_id, "processing")
    try:
        template_task = fetch_and_validate_template_task(template_task_id, task_type)
        amend_details = fetch_transaction_details(batch_id)
        cases = fetch_cases_for_batch(batch_id)
        drcs = {case["Case_Id"]: [case["DRC_Id"], case["RTOM"]] for case in cases if "Case_Id" in case and "DRC_Id" in case and "RTOM" in case}
        existing_drcs = {case["Case_Id"]: case["DRC_Id"] for case in cases if "Case_Id" in case and "DRC_Id" in case}

        for distribution in amend_details.get("array_of_distributions", []):
            receiver_drc = distribution.get("receiver_drc_id")
            donor_drc = distribution.get("donor_drc_id")
            rtom = distribution.get("rtom")
            transfer_value = distribution.get("transfer_count")

            with lock:
                if receiver_drc in active_amendments or donor_drc in active_amendments:
                    logger.error(f"Cannot process amendment for {receiver_drc} and {donor_drc}: One or both DRCs are already being amended.")
                    update_task_status(task_id, "failed")
                    return
                active_amendments.add(receiver_drc)
                active_amendments.add(donor_drc)

            try:
                updated_drcs, amend_description = balance_resources(drcs, receiver_drc, donor_drc, rtom, transfer_value)
                update_case_distribution_collection(updated_drcs, existing_drcs)
                update_summary_in_mongo(updated_drcs, batch_id)
            finally:
                with lock:
                    active_amendments.discard(receiver_drc)
                    active_amendments.discard(donor_drc)

        update_task_status(task_id, "completed")
    except Exception as e:
        logger.error(f"Error in Task ID {task_id}: {e}")
        update_task_status(task_id, "failed")

def process_tasks():
    """
    Processes open tasks in system_tasks that match the template_task collection.
    """
    try:
        logger.info("Querying system_tasks collection for open tasks...")
        open_tasks = list(system_task_collection.find({"task_status": "open", "task_type": "Case Amend Planning among DRC"}))
        logger.info(f"Found {len(open_tasks)} open tasks.")

        threads = [threading.Thread(target=process_single_batch, args=(task,)) for task in open_tasks]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")

# Entry point
if __name__ == "__main__":
    logger.info("Starting task processing...")
    process_tasks()
    logger.info("Task processing completed.")