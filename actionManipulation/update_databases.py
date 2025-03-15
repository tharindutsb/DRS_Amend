'''
update_databases.py file is as follows:

    Purpose: This script updates the case distribution collection and summary collection in the database.
    Created Date: 2025-03-01
    Created By:  T.S.Balasooriya (tharindutsb@gmail.com) , Pasan(pasanbathiya246@gmail.com),Amupama(anupamamaheepala999@gmail.com)
    Last Modified Date: 2025-03-15
    Modified By: T.S.Balasooriya (tharindutsb@gmail.com), Pasan(pasanbathiya246@gmail.com),Amupama(anupamamaheepala999@gmail.com)     
    Version: Python 3.9
    Dependencies: datetime, collections, utils.loggers, utils.connectDB, utils.Custom_Exceptions, utils.read_template_task_id_ini
    Notes:
'''
# update_databases.py
from datetime import datetime
from collections import defaultdict
from utils.loggers import get_logger
from utils.connectDB import get_collection
from utils.Custom_Exceptions import DatabaseUpdateError
from utils.read_template_task_id_ini import get_template_task_id

logger = get_logger("amend_status_logger")

def update_template_task_collection(case_distribution_batch_id):
    """
    Updates the Template_Task collection with the new TEMPLATE_TASK_ID and parameters for the "Case Amend Planning among DRC" type.
    Returns: (success, message or error)
    """
    try:
        template_task_collection = get_collection("Template_task")
        
        # Read the TEMPLATE_TASK_ID from the INI file
        ini_template_task_id = get_template_task_id()
        
        # Check if the task type "Case Amend Planning among DRC" exists in the collection
        existing_template_task = template_task_collection.find_one({
            "task_type": "Case Amend Planning among DRC"
        })
        
        if not existing_template_task:
            error_message = f"No template task found for 'Case Amend Planning among DRC'."
            logger.error(error_message)
            return False, error_message
        
        # Check if the existing Template_Task_Id matches the one from the INI file
        if existing_template_task["Template_Task_Id"] != ini_template_task_id:
            # Update the existing Template_Task_Id with the one from the INI file
            result = template_task_collection.update_one(
                {"task_type": "Case Amend Planning among DRC"},
                {
                    "$set": {
                        "Template_Task_Id": ini_template_task_id,
                        "parameters.Case_Distribution_Batch_ID": case_distribution_batch_id,
                        "last_updated_dtm": datetime.now()
                    }
                }
            )
            if result.modified_count == 0:
                error_message = f"Failed to update Template_Task_Id to {ini_template_task_id} in the Template_task collection for 'Case Amend Planning among DRC'."
                logger.error(error_message)
                return False, error_message
            logger.info(f"Template_Task_Id updated to {ini_template_task_id} in the Template_task collection for 'Case Amend Planning among DRC'.")
        else:
            # Update the parameters if the Template_Task_Id matches
            result = template_task_collection.update_one(
                {"task_type": "Case Amend Planning among DRC"},
                {
                    "$set": {
                        "parameters.Case_Distribution_Batch_ID": case_distribution_batch_id,
                        "last_updated_dtm": datetime.now()
                    }
                }
            )
            if result.modified_count == 0:
                error_message = f"Failed to update parameters for Template_Task_Id {ini_template_task_id} in the Template_task collection for 'Case Amend Planning among DRC'."
                logger.error(error_message)
                return False, error_message
            logger.info(f"Parameters updated for Template_Task_Id {ini_template_task_id} in the Template_task collection for 'Case Amend Planning among DRC'.")
        
        return True, "Template task collection updated successfully."
    except Exception as update_error:
        logger.error(f"Failed to update Template_Task collection: {update_error}")
        return False, str(update_error)

def update_case_distribution_collection(case_collection, updated_drcs, existing_drcs):
    """
    Updates the case distribution collection with the new DRC and resource values.
    Returns: (success, message or error, original_states)
    """
    try:
        logger.info("Updating case distribution collection...")
        
        # Store the original state for rollback
        original_states = {}
        for case_id, (new_drc, resource) in updated_drcs.items():
            if case_id in existing_drcs and existing_drcs[case_id] != new_drc:
                # Save the original DRC for rollback
                original_states[case_id] = existing_drcs[case_id]

                # Update the case distribution
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
                logger.debug(f"Update result for Case_Id {case_id}: {result.matched_count} documents matched, {result.modified_count} documents modified.")

        return True, original_states  # Success
    except Exception as update_error:
        logger.error(f"Failed to update case distribution collection: {update_error}")
        raise DatabaseUpdateError(f"Failed to update case distribution collection: {update_error}")

def rollback_case_distribution_collection(case_collection, original_states):
    """
    Rolls back the case distribution collection to its original state.
    Returns: (success, message or error)
    """
    try:
        logger.info("Rolling back case distribution collection...")
        for case_id, original_drc in original_states.items():
            case_collection.update_one(
                {"Case_Id": case_id},
                {
                    "$set": {
                        "NEW_DRC_ID": original_drc,
                        "Proceed_On": datetime.now(),
                        "Amend_Status": "Rolled Back",
                        "Amend_Description": f"Rolled back to {original_drc}"
                    }
                }
            )
        logger.info("Case distribution collection rolled back successfully.")
        return True, "Case distribution collection rolled back successfully."  # Success
    except Exception as rollback_error:
        logger.error(f"Failed to roll back case distribution collection: {rollback_error}")
        raise DatabaseUpdateError(f"Failed to roll back case distribution collection: {rollback_error}")

def update_summary_in_mongo(summary_collection, transaction_collection, updated_drcs, case_distribution_batch_id):
    """
    Updates the summary collection in MongoDB with the new counts after balancing.
    Also marks CRD_Distribution_Status and summery_status as 'close' once amendments are done.
    Returns: (success, message or error, original_counts)
    """
    try:
        logger.info("Updating summary in MongoDB...")
        
        # Store the original state for rollback
        original_counts = {}
        for case_id, (drc, rtom) in updated_drcs.items():
            original_counts[(drc, rtom)] = summary_collection.find_one(
                {"Case_Distribution_Batch_ID": case_distribution_batch_id, "DRC_Id": drc, "RTOM": rtom},
                {"Count": 1}
            )

        # Update the summary collection
        count_dict = defaultdict(lambda: defaultdict(int))
        for case_id, (drc, rtom) in updated_drcs.items():
            count_dict[drc][rtom] += 1

        for drc, resources in count_dict.items():
            for rtom, count in resources.items():
                summary_collection.update_one(
                    {
                        "Case_Distribution_Batch_ID": case_distribution_batch_id,
                        "DRC_Id": drc,
                        "RTOM": rtom
                    },
                    {"$set": {"Count": count}},
                    upsert=True
                )
        
        logger.info("Summary updated in MongoDB successfully.")

        # Mark CRD_Distribution_Status and summery_status as 'close'
        transaction_collection.update_one(
            {
                "Case_Distribution_Batch_ID": case_distribution_batch_id,
                "batch_seq_details.action_type": "amend",
                "batch_seq_details.CRD_Distribution_Status": "open",
                "summery_status": "open"
            },
            {
                "$set": {
                    "batch_seq_details.$.CRD_Distribution_Status": "close",
                    "summery_status": "close"
                }
            }
        )

        logger.info(f"Updated CRD_Distribution_Status to 'close' for Batch ID: {case_distribution_batch_id}")
        return True, original_counts  # Success
    except Exception as update_error:
        logger.error(f"Failed to update summary in MongoDB: {update_error}")
        raise DatabaseUpdateError(f"Failed to update summary in MongoDB: {update_error}")

def rollback_summary_in_mongo(summary_collection, original_counts, case_distribution_batch_id):
    """
    Rolls back the summary collection to its original state.
    Returns: (success, message or error)
    """
    try:
        logger.info("Rolling back summary in MongoDB...")
        for (drc, rtom), original_count in original_counts.items():
            summary_collection.update_one(
                {
                    "Case_Distribution_Batch_ID": case_distribution_batch_id,
                    "DRC_Id": drc,
                    "RTOM": rtom
                },
                {"$set": {"Count": original_count.get("Count", 0)}}
            )
        logger.info("Summary collection rolled back successfully.")
        return True, "Summary collection rolled back successfully."  # Success
    except Exception as rollback_error:
        logger.error(f"Failed to roll back summary in MongoDB: {rollback_error}")
        raise DatabaseUpdateError(f"Failed to roll back summary in MongoDB: {rollback_error}")