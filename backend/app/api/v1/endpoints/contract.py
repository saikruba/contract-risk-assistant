from fastapi import APIRouter, UploadFile, File
from pydantic import BaseModel
import os

from app.services.contract_service import analyze_contract
from app.services.vector_service import query_chunks, reset_db
from app.services.llm_service import call_llama

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
    results = query_chunks(req.query)

    # -------------------------------
    # Handle empty results
    # -------------------------------
    if not results:
        return {
            "query": req.query,
            "answer": "No relevant information found in the contract.",
            "results": []
        }

    # -------------------------------
    # Build context from retrieved chunks
    # -------------------------------
    context = "\n\n".join(
        f"Page {r.get('page', 'unknown')}: {r.get('text', '')}"
        for r in results
    )

    # -------------------------------
    # Prompt (Improved)
    # -------------------------------
    prompt = f"""
You are a legal contract assistant.

Answer the question based ONLY on the contract context below.

Question:
{req.query}

Context:
{context}

Instructions:
- Start with a direct answer (1 sentence summary)
- Then explain using bullet points
- Use simple, plain English (avoid legal jargon)
- Mention page numbers clearly
- Be concise but complete
- Do not repeat the same phrases
- Do not make up information
"""

    # -------------------------------
    # LLM Call
    # -------------------------------
    answer = call_llama(prompt)

    return {
        "query": req.query,
        "answer": answer,
        "results": results
    }


# -------------------------------
# Reset Endpoint
# -------------------------------
@router.post("/reset")
def reset_contract_db():
    reset_db()
    return {"message": "Reset successful"}
