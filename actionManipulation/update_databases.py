
'''
update database case distribution collection and summary collection update_database.py file is as follows:

    Purpose: This template is used for the DRC Amend.
    Created Date: 2025-01-08
    Created By:  T.S.Balasooriya (tharindutsb@gmail.com) , Pasan(pasanbathiya246@gmail.com),Amupama(anupamamaheepala999@gmail.com)
    Last Modified Date: 2024-01-19
    Modified By: T.S.Balasooriya (tharindutsb@gmail.com), Pasan(pasanbathiya246@gmail.com),Amupama(anupamamaheepala999@gmail.com)     
    Version: Node.js v20.11.1
    Dependencies: express
    Related Files: Case_controller.js
    Notes:
'''
# update_databases.py
from datetime import datetime
from collections import defaultdict
from utils.loggers import get_logger

logger = get_logger("amend_status_logger")

def update_case_distribution_collection(case_collection, updated_drcs, existing_drcs):
    """
    Updates the case distribution collection with the new DRC and resource values.
    Returns: (success, error, original_states)
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

        return True, None, original_states  # Success, no error, and original states for rollback
    except Exception as error_message:
        logger.error(f"Failed to update case distribution collection: {error_message}")
        return False, str(error_message), None  # Error and no original states

def rollback_case_distribution_collection(case_collection, original_states):
    """
    Rolls back the case distribution collection to its original state.
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
    except Exception as error_message:
        logger.error(f"Failed to roll back case distribution collection: {error_message}")

def update_summary_in_mongo(summary_collection, transaction_collection, updated_drcs, case_distribution_batch_id):
    """
    Updates the summary collection in MongoDB with the new counts after balancing.
    Also marks CRD_Distribution_Status and summery_status as 'close' once amendments are done.
    Returns: (success, error, original_counts)
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
        return True, None, original_counts  # Success, no error, and original counts for rollback
    except Exception as error_message:
        logger.error(f"Failed to update summary in MongoDB: {error_message}")
        return False, str(error_message), None  # Error and no original counts

def rollback_summary_in_mongo(summary_collection, original_counts, case_distribution_batch_id):
    """
    Rolls back the summary collection to its original state.
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
    except Exception as error_message:
        logger.error(f"Failed to roll back summary in MongoDB: {error_message}")