from app.schemas.contract_schema import ContractResponse
from langfuse import get_client
from app.core.config import settings
import time

# -------------------------------
# Fail-fast check
# -------------------------------
if not all([settings.LANGFUSE_PUBLIC_KEY, settings.LANGFUSE_SECRET_KEY, settings.LANGFUSE_BASE_URL]):
    raise ValueError("Langfuse credentials or base URL missing! Check .env")

# -------------------------------
# Initialize Langfuse client (reads .env automatically)
# -------------------------------
langfuse = get_client()

def analyze_contract(filename: str) -> ContractResponse:
    debug_logs = [
        "FUNCTION CALLED",
        f"Public Key: {settings.LANGFUSE_PUBLIC_KEY}",
        f"Secret Key: {settings.LANGFUSE_SECRET_KEY}",
        f"Base URL: {settings.LANGFUSE_BASE_URL}"
    ]

    try:
        with langfuse.start_as_current_observation(as_type="span", name="contract_analysis") as span:
            debug_logs.append("Span started")

            risk = "high"
            issues = ["missing clause"]

            span.update(output={
                "filename": filename,
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
        debug_logs.append(f"Langfuse error: {str(e)}")
        risk = "low"
        issues = ["missing clause"]

    return ContractResponse(
        filename=filename,
        risk=risk,
        issues=issues,
        debug=debug_logs
    )
