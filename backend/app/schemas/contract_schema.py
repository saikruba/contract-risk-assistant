from pydantic import BaseModel
from typing import List, Optional, Dict, Any


class ContractResponse(BaseModel):

    filename: str

    risk: str

    issues: List[str]

    summary: Optional[str] = None

    qa_results: Optional[List[Dict[str, Any]]] = None

    debug: List[str]
