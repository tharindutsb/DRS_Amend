from fastapi import APIRouter, HTTPException, Depends
from models.amend_model import AmendRequest
from services.amend_service import amend_resources
from logger.loggers import get_logger

logger = get_logger(__name__)

router = APIRouter()

@router.post("/amend")
async def amend(amend_request: AmendRequest):
    """
    Endpoint to handle the amendment request.
    
    :param amend_request: The amendment request containing rtom, donor_drc_id, receiver_drc_id, and transfer_count.
    :return: A response indicating the status of the amendment process.
    """
    try:
        # Log the incoming request
        logger.info(f"Received amendment request: {amend_request}")

        # Call the amend_resources function to process the request
        updated_drcs = amend_resources(amend_request)

        # Log the successful completion of the amendment process
        logger.info(f"Amendment process completed successfully. Updated DRCs: {updated_drcs}")

        # Return the response
        return {
            "status": "success",
            "message": "Amendment process completed successfully.",
            "updated_drcs": updated_drcs
        }
    except Exception as e:
        # Log the error
        logger.error(f"Error in amend endpoint: {e}")

        # Raise an HTTPException with a 400 status code and the error message
        raise HTTPException(status_code=400, detail=str(e))