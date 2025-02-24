from pydantic import BaseModel
from typing import Optional, List
from enum import Enum

class TaskStatus(str, Enum):
    OPEN = "open"
    IN_PROGRESS = "in-progress"
    COMPLETED = "completed"

class Distribution(BaseModel):
    drc: Optional[str] = None
    rulebase_count: Optional[int] = None
    rtom: Optional[str] = None
    donor_drc_id: Optional[str] = None
    receiver_drc_id: Optional[str] = None
    transfer_count: Optional[int] = None

class BatchSeqDetail(BaseModel):
    batch_seq: int
    created_dtm: str
    created_by: str
    action_type: str
    array_of_distributions: List[Distribution]
    batch_seq_rulebase_count: int
    task_status: TaskStatus = TaskStatus.OPEN

class AmendRequest(BaseModel):
    case_distribution_batch_id: str
    batch_seq_details: List[BatchSeqDetail]
    task_status: TaskStatus = TaskStatus.OPEN
