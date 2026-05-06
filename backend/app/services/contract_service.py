from app.schemas.contract_schema import ContractResponse
from app.services.vector_service import store_chunks
from app.core.config import settings

import traceback
from langfuse import get_client


from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

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
# PDF LOADER (REPLACED)
# -------------------------------
def extract_text_from_pdf(file_path: str):
    loader = PyPDFLoader(file_path)
    docs = loader.load()  # returns Document[]
    return docs


# -------------------------------
# CHUNKING (UPDATED)
# -------------------------------
def chunk_text(docs):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200
    )

    chunks = splitter.split_documents(docs)
    return chunks


# -------------------------------
# MAIN ANALYSIS FUNCTION
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
        docs = extract_text_from_pdf(file_path)
        debug_logs.append(f"Pages loaded: {len(docs)}")

        # ---------------- CHUNKING ----------------
        chunks = chunk_text(docs)[:50]
        debug_logs.append(f"Total chunks created: {len(chunks)}")

        # ---------------- VECTOR STORE ----------------
        store_chunks(
            [chunk.page_content for chunk in chunks],
            file_path
        )
        debug_logs.append("Stored chunks in DB")

        issues = [f"{len(chunks)} chunks stored in vector DB"]

        # ---------------- LANGFUSE ----------------
        with langfuse.start_as_current_observation(
            as_type="span",
            name="contract_analysis"
        ) as span:

            span.update(
                input={
                    "file_path": file_path,
                    "pages": len(docs),
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
