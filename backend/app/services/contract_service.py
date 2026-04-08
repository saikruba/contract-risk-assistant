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
        debug_logs.append(f"First 500 chars: {text[:500]}")

        # Step 2: Langfuse tracing
        with langfuse.start_as_current_observation(
            as_type="span",
            name="contract_analysis"
        ) as span:
            debug_logs.append("Span started")

            # Dummy logic (replace later)
            risk = "high"
            issues = ["missing clause"]

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
        issues = ["parsing failed"]

    return ContractResponse(
        filename=file_path,
        risk=risk,
        issues=issues,
        debug=debug_logs
    )
