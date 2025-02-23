from pydantic import BaseModel

class AmendRequest(BaseModel):
    rtom: str
    donor_drc_id: str
    receiver_drc_id: str
    transfer_count: int