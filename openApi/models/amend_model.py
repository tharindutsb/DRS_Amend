from pydantic import BaseModel
from typing import List, Optional

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

class AmendRequest(BaseModel):
    case_distribution_batch_id: int
    batch_seq_details: List[BatchSeqDetail]
    created_dtm: str
    created_by: str
    current_arrears_band: str
    rulebase_count: int
    rulebase_arrears_sum: int
    status: List[dict]
    drc_commision_rule: str
    forward_for_approvals_on: str
    approved_by: Optional[str] = None
    approved_on: Optional[str] = None
    proceed_on: Optional[str] = None
    tmp_record_remove_on: Optional[str] = None