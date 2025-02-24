from fastapi import APIRouter, HTTPException
from openApi.models.amend_model import AmendRequest, TaskStatus
from typing import Optional


from openApi.services.amend_service import amend_resources
from openApi.services.get_amend_plan import get_amend_plan
from openApi.services.balance_resources import balance_resources
from openApi.services.update_amend_drcs import update_drcs_in_mongo
from datetime import datetime
from utils.connectDB import get_db_connection
from logger.loggers import get_logger

router = APIRouter()
logger = get_logger(__name__)

@router.get("/task-status/{task_id}")
async def get_task_status(task_id: str):
    """
    Endpoint to get the status of a specific task
    
    :param task_id: The ID of the task to check
    :return: The current status of the task
    """
    try:
        # Get database connection
        db = get_db_connection()
        if db is None:
            logger.error("Failed to connect to database")
            raise HTTPException(status_code=500, detail="Database connection failed")

        # Access transactions collection
        collection = db["case_distribution_drc_transactions"]

        # Find the task by ID
        task = collection.find_one(
            {"batch_seq_details.batch_seq": task_id},
            {"batch_seq_details.$": 1}
        )

        if not task or "batch_seq_details" not in task:
            raise HTTPException(status_code=404, detail="Task not found")

        # Return the task status
        return {
            "task_id": task_id,
            "status": task["batch_seq_details"][0]["task_status"]
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting task status: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/amend")
async def create_amend(amend_request: AmendRequest):
    """
    Endpoint to create a new amendment plan
    """
    try:
        # Get database connection
        db = get_db_connection()
        if db is None:
            logger.error("Failed to connect to database")
            raise HTTPException(status_code=500, detail="Database connection failed")

        # Access transactions collection
        collection = db["case_distribution_drc_transactions"]

        # Find latest batch_seq
        latest_record = collection.find_one(sort=[("batch_seq_details.batch_seq", -1)])
        latest_batch_seq = latest_record["batch_seq_details"][-1]["batch_seq"] if latest_record else 0

        # Create new batch sequence detail
        new_batch_seq_detail = {
            "batch_seq": latest_batch_seq + 1,
            "created_dtm": datetime.utcnow().isoformat(),
            "created_by": "API",
            "action_type": "amend",
            "array_of_distributions": amend_request.batch_seq_details[0].array_of_distributions,
            "batch_seq_rulebase_count": amend_request.batch_seq_details[0].batch_seq_rulebase_count,
            "task_status": TaskStatus.OPEN

        }

        # Update MongoDB
        collection.update_one(
            {"case_distribution_batch_id": amend_request.case_distribution_batch_id},
            {"$push": {"batch_seq_details": new_batch_seq_detail}},
            upsert=True
        )

        logger.info(f"Created new amendment plan with batch_seq: {new_batch_seq_detail['batch_seq']}")
        return {"status": "success", "message": "Amendment plan created successfully"}

    except Exception as e:
        logger.error(f"Error creating amendment plan: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/process-amend")
async def process_amend(amend_request: AmendRequest):
    """
    Endpoint to process an amendment plan
    
    :param amend_request: The amendment request containing the batch details
    """

    try:
        # Get database connection
        db = get_db_connection()
        if db is None:
            logger.error("Failed to connect to database")
            raise HTTPException(status_code=500, detail="Database connection failed")

        # Access transactions collection
        collection = db["case_distribution_drc_transactions"]

        try:
            # Update task status to in-progress
            collection.update_one(
                {"case_distribution_batch_id": amend_request.case_distribution_batch_id},
                {"$set": {"batch_seq_details.$[elem].task_status": TaskStatus.IN_PROGRESS}},
                array_filters=[{"elem.batch_seq": amend_request.batch_seq_details[0].batch_seq}]
            )
            logger.info(f"Updated task status to IN_PROGRESS for batch {amend_request.batch_seq_details[0].batch_seq}")
        except Exception as status_error:
            logger.error(f"Failed to update task status to IN_PROGRESS: {str(status_error)}")
            raise HTTPException(status_code=500, detail=f"Task status update failed: {str(status_error)}")


        # Get amendment plan
        drcs, receiver_drc, donor_drc, rtom, transfer_value = get_amend_plan()

        if not all([drcs, receiver_drc, donor_drc, rtom, transfer_value]):
            raise ValueError("Invalid amendment plan data")

        # Balance resources
        updated_drcs = balance_resources(drcs, receiver_drc, donor_drc, rtom, transfer_value)
        if not updated_drcs:
            raise ValueError("Resource balancing failed")

        # Update MongoDB with amended DRCs
        update_drcs_in_mongo(
            updated_drcs,
            "Successful",
            f"Transferred {transfer_value} cases of {rtom} from {donor_drc} to {receiver_drc}"
        )

        try:
            # Update task status to completed
            collection.update_one(
                {"case_distribution_batch_id": amend_request.case_distribution_batch_id},
                {"$set": {"batch_seq_details.$[elem].task_status": TaskStatus.COMPLETED}},
                array_filters=[{"elem.batch_seq": amend_request.batch_seq_details[0].batch_seq}]
            )
            logger.info(f"Updated task status to COMPLETED for batch {amend_request.batch_seq_details[0].batch_seq}")
        except Exception as status_error:
            logger.error(f"Failed to update task status to COMPLETED: {str(status_error)}")
            raise HTTPException(status_code=500, detail=f"Task status update failed: {str(status_error)}")



        logger.info("Successfully processed amendment plan")
        return {
            "status": "success",
            "message": "Amendment process completed successfully",
            "updated_drcs": updated_drcs
        }

    except Exception as e:
        logger.error(f"Error processing amendment plan: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
