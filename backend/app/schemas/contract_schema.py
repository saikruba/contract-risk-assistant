from pydantic import BaseModel
from typing import List, Optional, Dict, Any


class ContractResponse(BaseModel):

    filename: str

    issues: List[str]

    summary: Optional[str] = None

    qa_results: Optional[List[Dict[str, Any]]] = None

    segment_analysis: Optional[List[Dict[str, Any]]] = []

    debug: List[str]
