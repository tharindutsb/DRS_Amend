from fastapi import APIRouter
from openApi.controllers.amend_controller import router as amend_router

router = APIRouter()
router.include_router(amend_router, prefix="/amend", tags=["Amend"])
