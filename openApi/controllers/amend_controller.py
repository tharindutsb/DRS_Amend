from fastapi import APIRouter, HTTPException
from openApi.models.amend_model import AmendRequest
from openApi.services.amend_service import add_amendment_record

router = APIRouter()

@router.post("/add_amend")
async def add_amend(amendment: AmendRequest):
    try:
        result = add_amendment_record(amendment.dict())
        if "error" in result:
            raise HTTPException(status_code=500, detail=result["error"])
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"❌ Unexpected error: {str(e)}")
