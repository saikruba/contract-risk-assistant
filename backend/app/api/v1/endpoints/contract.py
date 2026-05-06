from fastapi import APIRouter, UploadFile, File
from pydantic import BaseModel
import os

from app.services.contract_service import analyze_contract
from app.services.vector_service import query_chunks, reset_db
from app.services.llm_service import call_llama

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

    # handle empty results
    if not results:
        return {
            "query": req.query,
            "answer": "No relevant information found in the contract.",
            "results": []
        }

    # build context
    context = "\n\n".join([
        f"Page {r['page']}: {r['text']}"
        for r in results
    ])

    prompt = f"""
Answer the question based on the contract below.

Question:
{req.query}

Context:
{context}

Instructions:
- Answer in plain English
- Mention page numbers when relevant
- Keep it concise
"""

    answer = call_llama(prompt)

    return {
        "query": req.query,
        "answer": answer,
        "results": results
    }
    
@router.post("/reset")
def reset_contract_db():
    reset_db()
    return {"message": "Reset successful"}
    

