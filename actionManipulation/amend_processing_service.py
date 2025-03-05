# /* 
#     Purpose: This template is used for the DRC Amend.
#     Created Date: 2025-01-08
#     Created By:  T.S.Balasooriya (tharindutsb@gmail.com) , Pasan(pasanbathiya246@gmail.com),Amupama(anupamamaheepala999@gmail.com)
#     Last Modified Date: 2024-01-19
#     Modified By: T.S.Balasooriya (tharindutsb@gmail.com), Pasan(pasanbathiya246@gmail.com),Amupama(anupamamaheepala999@gmail.com)     
#     Version: Node.js v20.11.1
#     Dependencies: express
#     Related Files: Case_controller.js
#     Notes:  
# */

from datetime import datetime
from collections import defaultdict
import threading
from utils.connectDB import get_db_connection, initialize_collections
from logger.loggers import get_logger  # Import the logger

# Initialize logger
logger = get_logger("amend_status_logger")  # Use logger

# Initialize MongoDB collections
collections = initialize_collections( get_db_connection())
case_collection = collections["case_collection"]
transaction_collection = collections["transaction_collection"]
summary_collection = collections["summary_collection"]
system_task_collection = collections["system_task_collection"]
template_task_collection = collections["template_task_collection"]

# Locking mechanism for parallel processing
lock = threading.Lock()
active_amendments = set()  # Tracks DRCs currently being amended

def update_task_status(system_task_collection, task_id, status):
    """
    Updates the status of a task in the system_task collection.
    """
    try:
        logger.info(f"Updating task status to '{status}' for Task ID {task_id}...")
        system_task_collection.update_one(
            {"Task_Id": task_id},
            {
                "$set": {
                    "task_status": status,
                    "last_updated": datetime.now()
                }
            }
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
        logger.info(f"Querying Case_distribution_drc_transactions collection for Batch ID: {case_distribution_batch_id}...")
        
        # Fetch the transaction record for the given batch ID
        transaction_record = transaction_collection.find_one({
            "Case_Distribution_Batch_ID": case_distribution_batch_id
        })
        
        # Check if the transaction record exists
        if not transaction_record:
            raise ValueError(f"No transaction record found for Batch ID {case_distribution_batch_id}.")

        # Extract batch_seq_details
        batch_seq_details = transaction_record.get("batch_seq_details", [])
        
        # Find the amend action in batch_seq_details
        amend_details = None
        for batch_seq in batch_seq_details:
            if batch_seq.get("action_type") == "amend":
                amend_details = batch_seq
                break

        # Check if amend action exists
        if not amend_details:
            raise ValueError(f"No amend action found for Batch ID {case_distribution_batch_id}.")

        # Extract array_of_distributions
        array_of_distributions = amend_details.get("array_of_distributions", [])
        
        # Check if array_of_distributions exists and is not empty
        if not array_of_distributions:
            raise ValueError(f"No array_of_distributions found for amend action in Batch ID {case_distribution_batch_id}.")

        # Validate mandatory fields in each distribution
        for distribution in array_of_distributions:
            if not all(key in distribution for key in ["rtom", "donor_drc_id", "receiver_drc_id", "transfer_count"]):
                raise ValueError(f"Missing mandatory fields in array_of_distributions for Batch ID {case_distribution_batch_id}.")

        # Return the amend_details for further processing
        return amend_details

    except Exception as e:
        logger.error(f"Failed to fetch or validate transaction details: {e}")
        raise
    
# def fetch_cases_for_batch(case_collection, case_distribution_batch_id):
#     """
#     Fetches cases for the given batch ID from the DRS.Tmp_Case_Distribution_DRC collection.
#     """
#     try:
#         logger.info("Fetching relevant cases from DRS.Tmp_Case_Distribution_DRC collection...")
#         cases = list(case_collection.find({
#             "Case_Distribution_Batch_ID": case_distribution_batch_id
#         }))
#         logger.info(f"Found {len(cases)} cases for Batch ID {case_distribution_batch_id}.")
#         return cases
#     except Exception as e:
#         logger.error(f"Failed to fetch cases for batch: {e}")
#         raise
def fetch_cases_for_batch(case_collection, case_distribution_batch_id):
    """
    Fetches cases that match the given batch ID from the DRS.Tmp_Case_Distribution_DRC collection
    and prints the retrieved data.
    """
    try:
        logger.info(f"Fetching cases for Batch ID {case_distribution_batch_id} from DRS.Tmp_Case_Distribution_DRC collection...")
        
        # Query the collection for cases that match the given batch ID
        cases_cursor = case_collection.find({"Case_Distribution_Batch_ID": case_distribution_batch_id})

        cases = list(cases_cursor)  # Convert cursor to a list
        logger.info(f"Found {len(cases)} cases for Batch ID {case_distribution_batch_id}.")
        
        # Print retrieved data
        if cases:
            logger.info("Printing retrieved cases:")
            for case in cases:
                print(case)  # Print each document in the result
        else:
            logger.info("No cases found for the given Batch ID.")

        return cases
    except Exception as e:
        logger.error(f"Failed to fetch cases for batch ID {case_distribution_batch_id}: {e}")
        raise



def balance_resources(drcs, receiver_drc, donor_drc, rtom, transfer_value):
    """
    Balances resources between DRCs based on the given logic.
    """
    resource_tracker = defaultdict(lambda: defaultdict(list))
    for case_id, (drc, resource) in drcs.items():
        resource_tracker[drc][resource].append(case_id)

    try:
        # Step 1: Check if receiver_drc and donor_drc exist
        if receiver_drc not in resource_tracker or donor_drc not in resource_tracker:
            raise ValueError(f"One of the DRCs ({receiver_drc} or {donor_drc}) does not exist.")

        # Step 2: Check if rtom exists in both receiver_drc and donor_drc
        if rtom not in resource_tracker[receiver_drc] or rtom not in resource_tracker[donor_drc]:
            raise ValueError(f"The resource {rtom} does not exist in both {receiver_drc} and {donor_drc}.")

        # Step 3: Check if donor_drc can donate without going below 20% of its resources
        donor_resource_count = len(resource_tracker[donor_drc][rtom])
        if donor_resource_count > 0 and (donor_resource_count - transfer_value < 0.2 * donor_resource_count):
            raise ValueError(f"Insufficient resources in {donor_drc} for the Donate.")

        # Step 4: Check if receiver_drc can receive without going below 20% of its resources
        receiver_resource_count = len(resource_tracker[receiver_drc][rtom])
        if receiver_resource_count > 0 and (receiver_resource_count - transfer_value < 0.2 * receiver_resource_count):
            raise ValueError(f"Insufficient resources in {receiver_drc} for the Balance.")

        # Step 5: Perform the transfer
        for _ in range(transfer_value):
            case_id = resource_tracker[donor_drc][rtom].pop(0)
            resource_tracker[receiver_drc][rtom].append(case_id)

        # Step 6: Balance back using round-robin method
        common_resources = set(resource_tracker[receiver_drc].keys()).intersection(set(resource_tracker[donor_drc].keys()))
        common_resources.discard(rtom)  # Exclude the rtom from balancing back

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

        # Convert resource_tracker back to the original drcs format
        updated_drcs = {}
        for drc, resources in resource_tracker.items():
            for resource, case_ids in resources.items():
                for case_id in case_ids:
                    updated_drcs[case_id] = [drc, resource]

        return updated_drcs, f"Successfully transferred {transfer_value} cases of {rtom} from {donor_drc} to {receiver_drc}."

    except Exception as e:
        return drcs, str(e)

def update_case_distribution_collection(case_collection, updated_drcs, existing_drcs):
    """
    Updates the DRS.Tmp_Case_Distribution_DRC collection with the new DRC and resource values.
    """
    try:
        logger.info("Updating DRS.Tmp_Case_Distribution_DRC collection...")
        for case_id, (new_drc, resource) in updated_drcs.items():
            if case_id in existing_drcs and existing_drcs[case_id] != new_drc:
                result = case_collection.update_one(
                    {"Case_Id": case_id},
                    {
                        "$set": {
                            "NEW_DRC_ID": new_drc,
                            "Proceed_On": datetime.now(),
                            "Amend_Status": "Completed",
                            "Amend_Description": f"Transferred to {new_drc}"
                        }
                    }
                )
                logger.info(f"Update result for Case_Id {case_id}: {result.matched_count} documents matched, {result.modified_count} documents modified.")
    except Exception as e:
        logger.error(f"Failed to update DRS.Tmp_Case_Distribution_DRC collection: {e}")
        raise

def update_summary_in_mongo(updated_drcs, case_distribution_batch_id):
    """
    Updates the Case_Distribution_DRC_Summary collection in MongoDB with the new counts after balancing.
    """
    try:
        # Create a dictionary to count the number of cases for each (DRC_Id, RTOM) pair
        count_dict = defaultdict(lambda: defaultdict(int))
        for case_id, (drc, rtom) in updated_drcs.items():
            count_dict[drc][rtom] += 1

        # Update the summary collection with the new counts
        for drc, resources in count_dict.items():
            for rtom, count in resources.items():
                summary_collection.update_one(
                    {
                        "Case_Distribution_Batch_ID": case_distribution_batch_id,
                        "DRC_Id": drc,
                        "RTOM": rtom
                    },
                    {
                        "$set": {"Count": count}
                    },
                    upsert=True  # Create a new document if it doesn't exist
                )
        logger.info("Summary updated in MongoDB successfully.")
    except Exception as e:
        logger.error(f"Failed to update summary in MongoDB: {e}")
        raise

def process_single_batch(task):
    """
    Processes a single batch for the given task.
    """
    task_id = task["Task_Id"]
    template_task_id = task["Template_Task_Id"]
    task_type = task["task_type"]
    case_distribution_batch_id = task["parameters"]["Case_Distribution_Batch_ID"]

    # Log the task details
    logger.info(f"Processing Task ID {task_id}:")
    logger.info(f"  Template_Task_Id: {template_task_id}")
    logger.info(f"  task_type: {task_type}")
    logger.info(f"  Case_Distribution_Batch_ID: {case_distribution_batch_id}")

    # Step 1: Update task status to "processing"
    update_task_status(system_task_collection, task_id, "processing")

    # Step 2: Fetch and validate template task
    try:
        template_task = fetch_and_validate_template_task(template_task_collection, template_task_id, task_type)
    except ValueError as e:
        logger.error(f"Error in Task ID {task_id}: {e}")
        update_task_status(system_task_collection, task_id, "failed")
        return

    # Step 3: Fetch transaction details
    try:
        amend_details = fetch_transaction_details(transaction_collection, case_distribution_batch_id)
    except ValueError as e:
        logger.error(f"Error in Task ID {task_id}: {e}")
        update_task_status(system_task_collection, task_id, "failed")
        return

    # Step 4: Fetch cases for the batch
    try:
        cases = fetch_cases_for_batch(case_collection, case_distribution_batch_id)
    except Exception as e:
        logger.error(f"Error in Task ID {task_id}: {e}")
        update_task_status(system_task_collection, task_id, "failed")
        return

    # Convert cases to a dictionary format for balancing logic
    drcs = {}
    existing_drcs = {}  # Dictionary to store existing DRC_Id values for quick lookup
    for case in cases:
        if "Case_Id" in case and "DRC_Id" in case and "RTOM" in case:
            drcs[case["Case_Id"]] = [case["DRC_Id"], case["RTOM"]]
            existing_drcs[case["Case_Id"]] = case["DRC_Id"]  # Store existing DRC_Id for comparison
        else:
            logger.error(f"Skipping case due to missing fields: {case}")
            continue

    # Step 5: Fetch transaction details and process amendments
    logger.info("Fetching transaction details...")
    array_of_distributions = amend_details.get("array_of_distributions", [])
    for distribution in array_of_distributions:
        receiver_drc = distribution.get("receiver_drc_id")
        donor_drc = distribution.get("donor_drc_id")
        rtom = distribution.get("rtom")
        transfer_value = distribution.get("transfer_count")

        # Step 6: Acquire lock to prevent overlapping amendments
        with lock:
            if receiver_drc in active_amendments or donor_drc in active_amendments:
                logger.error(f"Cannot process amendment for {receiver_drc} and {donor_drc}: One or both DRCs are already being amended.")
                update_task_status(system_task_collection, task_id, "failed")
                return

            # Mark DRCs as active
            active_amendments.add(receiver_drc)
            active_amendments.add(donor_drc)

        try:
            # Step 7: Run the balancing logic
            logger.info("Running balancing logic...")
            updated_drcs, amend_description = balance_resources(drcs, receiver_drc, donor_drc, rtom, transfer_value)

            # Log the updated_drcs for debugging
            logger.info(f"Updated DRCs: {updated_drcs}")

            # Step 8: Update DRS.Tmp_Case_Distribution_DRC collection
            update_case_distribution_collection(case_collection, updated_drcs, existing_drcs)

            # Step 9: Update DRS_Database.Case_Distribution_DRC_Summary collection
            update_summary_in_mongo(updated_drcs, case_distribution_batch_id)

        finally:
            # Release lock and mark DRCs as inactive
            with lock:
                active_amendments.discard(receiver_drc)
                active_amendments.discard(donor_drc)

    # Step 10: Update task status to "completed"
    update_task_status(system_task_collection, task_id, "completed")
    logger.info(f"Task ID {task_id} completed successfully.")
  

def process_tasks():
    """
    Processes open tasks in system_tasks that match the template_task collection.
    Ensures all functions work with a single batch ID and updates task status accordingly.
    """
    try:
        # Step 1: Query system_tasks collection for open tasks of type "Case Amend Planning among DRC"
        logger.info("Querying system_tasks collection for open tasks...")
        open_tasks = list(system_task_collection.find({
            "task_status": "open",
            "task_type": "Case Amend Planning among DRC"
        }))
        logger.info(f"Found {len(open_tasks)} open tasks.")

        # Step 2: Process tasks in parallel using threads
        threads = []
        for task in open_tasks:
            thread = threading.Thread(target=process_single_batch, args=(task,))
            threads.append(thread)
            thread.start()

        # Wait for all threads to complete
        for thread in threads:
            thread.join()

    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")