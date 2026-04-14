from fastapi import APIRouter, UploadFile, File
from pydantic import BaseModel
import os

from app.services.contract_service import analyze_contract
from app.services.vector_service import query_chunks

router = APIRouter()

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.post("/upload-contract")
async def upload_contract(file: UploadFile = File(...)):
    file_path = os.path.join(UPLOAD_DIR, file.filename)

    with open(file_path, "wb") as f:
        f.write(await file.read())

    return analyze_contract(file_path)


# -------------------------------
# Query Endpoint
# -------------------------------

class QueryRequest(BaseModel):
    query: str


@router.post("/query")
def query_contract(req: QueryRequest):
    results = query_chunks(req.query)

    return {
        "query": req.query,
        "results": results
    }
