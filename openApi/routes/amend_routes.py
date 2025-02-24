from fastapi import APIRouter
from openApi.controllers.amend_controller import create_amend, process_amend, get_task_status



router = APIRouter()

# Register controller endpoints
router.add_api_route("/amend", create_amend, methods=["POST"])
router.add_api_route("/process-amend", process_amend, methods=["GET"])
router.add_api_route("/task-status/{task_id}", get_task_status, methods=["GET"])
