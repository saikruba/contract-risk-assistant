from app.schemas.contract_schema import ContractResponse
from app.services.vector_service import store_chunks
from langfuse import get_client
from app.core.config import settings
import pdfplumber
import time

# Langfuse Setup
if not all([
    settings.LANGFUSE_PUBLIC_KEY,
    settings.LANGFUSE_SECRET_KEY,
    settings.LANGFUSE_BASE_URL
]):
    raise ValueError("Langfuse credentials missing! Check .env")

langfuse = get_client()


def extract_text_from_pdf(file_path: str) -> str:
    text = ""
    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    return text


def chunk_text(text: str, chunk_size: int = 500, overlap: int = 50):
    chunks = []
    start = 0

    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]
        chunks.append(chunk)

        start += chunk_size - overlap

    return chunks


def analyze_contract(file_path: str) -> ContractResponse:
    debug_logs = [
        "FUNCTION CALLED",
        f"File Path: {file_path}"
    ]

    try:
        text = extract_text_from_pdf(file_path)
        debug_logs.append(f"Extracted text length: {len(text)}")

        chunks = chunk_text(text)
        chunks = chunks[:50]

        debug_logs.append(f"Total chunks created: {len(chunks)}")

        store_chunks(chunks, file_path)
        debug_logs.append("Stored chunks in DB")

        # ✅ REMOVE LANGFUSE FOR NOW
        risk = "low"
        issues = [f"{len(chunks)} chunks stored"]

    except Exception as e:
        import traceback
        error_msg = str(e)
        trace = traceback.format_exc()

        print("❌ ERROR:", trace)

        debug_logs.append(error_msg)
        debug_logs.append(trace)

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
