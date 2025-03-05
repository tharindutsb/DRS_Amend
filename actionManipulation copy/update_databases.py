from datetime import datetime
from collections import defaultdict
from logger.loggers import get_logger

logger = get_logger("update_databases_logger")

def update_case_distribution_collection(case_collection, updated_drcs, existing_drcs):
    """
    Updates the case distribution collection with the new DRC and resource values.
    """
    try:
        logger.info("Updating case distribution collection...")
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
        logger.error(f"Failed to update case distribution collection: {e}")
        raise

def update_summary_in_mongo(summary_collection, updated_drcs, case_distribution_batch_id):
    """
    Updates the summary collection in MongoDB with the new counts after balancing.
    """
    try:
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
    except Exception as e:
        logger.error(f"Failed to update summary in MongoDB: {e}")
        raise