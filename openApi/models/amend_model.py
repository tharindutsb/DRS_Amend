from pydantic import BaseModel
from typing import List, Optional

class Distribution(BaseModel):
    rtom: str
    donor_drc_id: str
    receiver_drc_id: str
    transfer_count: int

class CaseAmendment(BaseModel):
    batch_seq: Optional[int] = None
    created_by: str
    action_type: str
    array_of_distributions: List[Distribution]
