from pydantic import BaseModel
from typing import List

class ContractResponse(BaseModel):
    filename: str
    risk: str
    issues: List[str]
    debug: List[str]
