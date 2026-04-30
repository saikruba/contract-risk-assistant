from fastapi import APIRouter, UploadFile, File
from pydantic import BaseModel
import os
import uuid

from app.services.contract_service import analyze_contract
from app.agents.qa_agent import qa_agent

router = APIRouter()

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.post("/upload-contract")
async def upload_contract(file: UploadFile = File(...)):
    if not file.filename.endswith(".pdf"):
        return {"error": "Only PDF allowed"}

    unique_name = f"{uuid.uuid4()}_{file.filename}"
    file_path = os.path.join(UPLOAD_DIR, unique_name)

    content = await file.read()
    with open(file_path, "wb") as f:
        f.write(content)

    return analyze_contract(file_path)


class QueryRequest(BaseModel):
    query: str
    filename: str


@router.post("/query")
def query_contract(req: QueryRequest):
    return qa_agent(req.query, req.filename)
