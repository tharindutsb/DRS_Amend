# from fastapi import APIRouter, HTTPException
# from services.amend_service import create_amend_plan, process_amend_plan
# from models.amend_model import AmendmentRequest

# router = APIRouter()

# @router.post("/create-amend-plan")
# async def create_amend_plan_endpoint(request: AmendmentRequest):
#     """
#     Endpoint to create an amendment plan.
#     """
#     try:
#         # Call the service to create the amendment plan and store it in the database
#         plan_id = create_amend_plan(request.rtom, request.donor_drc_id, request.receiver_drc_id, request.transfer_count)
#         return {"message": "Amendment plan created successfully", "plan_id": plan_id}
    
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Error creating amendment plan: {str(e)}")

# @router.post("/process-amend-plan")
# async def process_amend_plan_endpoint(plan_id: str):
#     """
#     Endpoint to process the amendment plan.
#     """
#     try:
#         result = process_amend_plan(plan_id)
#         return result
    
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Error processing amendment plan: {str(e)}")
