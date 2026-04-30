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
            t = page.extract_text()
            if t:
                text += t + "\n"
    return text


def chunk_text(text: str, chunk_size=500, overlap=100):
    chunks = []
    start = 0

    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start += chunk_size - overlap

    return chunks


def analyze_contract(file_path: str) -> ContractResponse:
    debug_logs = []

    try:
        text = extract_text_from_pdf(file_path)
        debug_logs.append(f"text length: {len(text)}")

        chunks = chunk_text(text)[:50]
        debug_logs.append(f"chunks: {len(chunks)}")

        # ✅ IMPORTANT: use consistent filename
        store_chunks(chunks, file_path)

        if langfuse:
            try:
                with langfuse.start_as_current_observation(
                    as_type="span",
                    name="contract_analysis"
                ) as span:
                    span.update(output={"file": file_path})
            except Exception as e:
                debug_logs.append(f"Langfuse error: {str(e)}")

        risk = "low"
        issues = ["Stored in vector DB"]

    except Exception as e:
        debug_logs.append(str(e))
        risk = "low"
        issues = ["processing failed"]

    return ContractResponse(
        filename=file_path,
        risk=risk,
        issues=issues,
        debug=debug_logs
    )
