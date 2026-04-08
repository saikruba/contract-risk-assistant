from app.schemas.contract_schema import ContractResponse
from langfuse import get_client
from app.core.config import settings
import pdfplumber
import time

# -------------------------------
# Langfuse Setup
# -------------------------------
if not all([
    settings.LANGFUSE_PUBLIC_KEY,
    settings.LANGFUSE_SECRET_KEY,
    settings.LANGFUSE_BASE_URL
]):
    raise ValueError("Langfuse credentials missing! Check .env")

langfuse = get_client()

# -------------------------------
# PDF Extraction (Parsing)
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
# Chunking Function
# -------------------------------
def chunk_text(text: str, chunk_size: int = 800, overlap: int = 100):
    chunks = []
    start = 0

    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]
        chunks.append(chunk)

        start += chunk_size - overlap

    return chunks

# -------------------------------
# Main Function
# -------------------------------
def analyze_contract(file_path: str) -> ContractResponse:
    debug_logs = [
        "FUNCTION CALLED",
        f"File Path: {file_path}"
    ]

    try:
        # Step 1: Extract text
        text = extract_text_from_pdf(file_path)
        debug_logs.append(f"Extracted text length: {len(text)}")
        debug_logs.append(f"First 801 chars: {text[:801]}")

        # Step 2: Chunk text
        chunks = chunk_text(text)
        debug_logs.append(f"Total chunks created: {len(chunks)}")
        debug_logs.append(f"First chunk preview: {chunks[0][:1000]}")

        # Step 3: Langfuse tracing
        with langfuse.start_as_current_observation(
            as_type="span",
            name="contract_analysis"
        ) as span:
            debug_logs.append("Span started")

            # Dummy logic (will improve later)
            risk = "low"
            issues = [f"{len(chunks)} chunks created"]

            span.update(output={
                "filename": file_path,
                "risk": risk,
                "issues": issues
            })

        try:
            langfuse.flush()
        except Exception as e:
            debug_logs.append(f"Flush failed: {str(e)}")
        finally:
            time.sleep(1)

        debug_logs.append("TRACE SENT")

    except Exception as e:
        debug_logs.append(f"Error: {str(e)}")
        risk = "low"
        issues = ["processing failed"]

    return ContractResponse(
        filename=file_path,
        risk=risk,
        issues=issues,
        debug=debug_logs
    )
