from app.schemas.contract_schema import ContractResponse
from app.services.vector_service import store_chunks
from app.core.config import settings

import pdfplumber
import traceback
from langfuse import get_client

# -------------------------------
# Langfuse Setup (KEEP OLD WORKING STYLE)
# -------------------------------
if not all([
    settings.LANGFUSE_PUBLIC_KEY,
    settings.LANGFUSE_SECRET_KEY,
    settings.LANGFUSE_BASE_URL
]):
    raise ValueError("Langfuse credentials missing! Check .env")

langfuse = get_client()


# -------------------------------
# PDF Extraction
# -------------------------------
def extract_text_from_pdf(file_path: str) -> str:
    text = ""
    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    return text


# -------------------------------
# Chunking
# -------------------------------
def chunk_text(text: str, chunk_size: int = 500, overlap: int = 50):
    chunks = []
    start = 0

    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start += chunk_size - overlap

    return chunks


# -------------------------------
# MAIN ANALYSIS FUNCTION (FIXED LANGFUSE)
# -------------------------------
def analyze_contract(file_path: str) -> ContractResponse:

    debug_logs = [
        "FUNCTION CALLED",
        f"File Path: {file_path}"
    ]

    risk = "low"
    issues = []

    try:
        # ---------------- PDF ----------------
        text = extract_text_from_pdf(file_path)
        debug_logs.append(f"Extracted text length: {len(text)}")

        # ---------------- CHUNKING ----------------
        chunks = chunk_text(text)[:50]
        debug_logs.append(f"Total chunks created: {len(chunks)}")

        # ---------------- VECTOR STORE ----------------
        store_chunks(chunks, file_path)
        debug_logs.append("Stored chunks in DB")

        issues = [f"{len(chunks)} chunks stored in vector DB"]

        # ---------------- LANGFUSE (OLD WORKING STYLE) ----------------
        with langfuse.start_as_current_observation(
            as_type="span",
            name="contract_analysis"
        ) as span:

            span.update(
                input={
                    "file_path": file_path,
                    "text_length": len(text),
                    "chunks": len(chunks)
                },
                output={
                    "risk": risk,
                    "issues": issues
                }
            )

        try:
            langfuse.flush()
        except Exception as e:
            debug_logs.append(f"Flush failed: {str(e)}")

        debug_logs.append("TRACE SENT")

    except Exception as e:
        error_msg = str(e)
        trace_error = traceback.format_exc()

        debug_logs.append(error_msg)
        debug_logs.append(trace_error)

        return ContractResponse(
            filename=file_path,
            risk="error",
            issues=[error_msg],
            debug=debug_logs
        )

    return ContractResponse(
        filename=file_path,
        risk=risk,
        issues=issues,
        debug=debug_logs
    )
