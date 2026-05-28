from fastapi import APIRouter, UploadFile, File
from pydantic import BaseModel
import os

from app.services.contract_service import analyze_contract
from app.services.vector_service import reset_db
from app.services.agents.qa_agent import run_qa_agent

router = APIRouter()

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


# -------------------------------
# Upload Endpoint
# -------------------------------
@router.post("/upload-contract")
async def upload_contract(file: UploadFile = File(...)):
    file_path = os.path.join(UPLOAD_DIR, file.filename)

    with open(file_path, "wb") as f:
        f.write(await file.read())

    return analyze_contract(file_path)


# -------------------------------
# Query Schema
# -------------------------------
class QueryRequest(BaseModel):
    query: str


# -------------------------------
# Query Endpoint (QA Agent)
# -------------------------------
@router.post("/query")
def query_contract(req: QueryRequest):

    qa_result = run_qa_agent(req.query)

    return {
        "query": req.query,
        "answer": qa_result["answer"],
        "results": qa_result["references"]
    }

# -------------------------------
# Reset Endpoint
# -------------------------------
@router.post("/reset")
def reset_contract_db():
    reset_db()
    return {"message": "Reset successful"}
