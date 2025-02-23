from fastapi import APIRouter, HTTPException
from models.amend_model import AmendRequest, Distribution, BatchSeqDetail
from services.get_amend_plan import get_amend_plan
from services.balance_resources import balance_resources
from services.update_amend_drcs import update_drcs_in_mongo
from datetime import datetime
from utils.connectDB import get_db_connection

router = APIRouter()

@router.post("/amend")
async def create_amend(amend_request: AmendRequest):
    """
    Endpoint to add a new amendment plan to the database.
    Automatically increments the batch_seq.
    """
    try:
        # Get the database connection
        db = get_db_connection()
        if not db:
            raise Exception("Failed to connect to the database.")

        # Access the case_distribution_drc_transactions collection
        collection = db["case_distribution_drc_transactions"]

        # Find the latest batch_seq
        latest_record = collection.find_one(sort=[("batch_seq_details.batch_seq", -1)])
        if latest_record:
            latest_batch_seq = latest_record["batch_seq_details"][-1]["batch_seq"]
        else:
            latest_batch_seq = 0

        # Increment the batch_seq
        new_batch_seq = latest_batch_seq + 1

        # Add the new amendment plan to the batch_seq_details
        new_batch_seq_detail = {
            "batch_seq": new_batch_seq,
            "created_dtm": datetime.utcnow().isoformat(),
            "created_by": "API",
            "action_type": "amend",
            "array_of_distributions": amend_request.batch_seq_details[0].array_of_distributions,
            "batch_seq_rulebase_count": amend_request.batch_seq_details[0].batch_seq_rulebase_count
        }

        # Update the document in MongoDB
        collection.update_one(
            {"case_distribution_batch_id": amend_request.case_distribution_batch_id},
            {
                "$push": {
                    "batch_seq_details": new_batch_seq_detail
                }
            },
            upsert=True
        )

        return {"status": "success", "message": "Amendment plan added successfully."}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/process-amend")
async def process_amend():
    """
    Endpoint to process the amendment plan using get_amend_plan, balance_resources, and update_drcs_in_mongo.
    """
    try:
        # Fetch the amendment plan
        drcs, receiver_drc, donor_drc, rtom, transfer_value = get_amend_plan()

        # Perform the balance operation
        updated_drcs = balance_resources(drcs, receiver_drc, donor_drc, rtom, transfer_value)

        # Update MongoDB with the new DRCs
        update_drcs_in_mongo(updated_drcs, "Successful", f"Transferred {transfer_value} cases of {rtom} from {donor_drc} to {receiver_drc}.")

        return {"status": "success", "message": "Amendment process completed successfully.", "updated_drcs": updated_drcs}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))