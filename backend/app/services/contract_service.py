from app.schemas.contract_schema import ContractResponse
from app.services.vector_service import store_chunks
from app.services.agents.orchestrator import (
    run_multi_agent_pipeline
)
from app.core.config import settings

import traceback
from langfuse import get_client

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.core.database import SessionLocal
from app.models.review_model import ContractReview

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
# PDF LOADER
# -------------------------------
def extract_text_from_pdf(file_path: str):

    loader = PyPDFLoader(file_path)

    docs = loader.load()

    return docs


# -------------------------------
# CHUNKING
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


    issues = []

    summary = None

    qa_results = []

    try:

        # -------------------------------
        # PDF LOAD
        # -------------------------------
        docs = extract_text_from_pdf(file_path)

        debug_logs.append(
            f"Pages loaded: {len(docs)}"
        )

        # -------------------------------
        # CHUNKING
        # -------------------------------
        chunks = chunk_text(docs)[:20]

        debug_logs.append(
            f"Total chunks created: {len(chunks)}"
        )

        # -------------------------------
        # VECTOR STORE
        # -------------------------------
        store_chunks(
            [chunk.page_content for chunk in chunks],
            [
                {
                    "source": file_path,
                    "page": chunk.metadata.get("page", 0) + 1
                }
                for chunk in chunks
            ]
        )

        debug_logs.append("Stored chunks in DB")

        # -------------------------------
        # FULL CONTRACT TEXT
        # -------------------------------
        full_text = "\n".join(
            [chunk.page_content for chunk in chunks]
        )

        debug_logs.append(
            f"Risk analysis input length: {len(full_text)}"
        )

        # -------------------------------
        # MULTI-AGENT ORCHESTRATOR
        # -------------------------------
        debug_logs.append(
            "Running multi-agent pipeline"
        )

        pipeline_output = run_multi_agent_pipeline(
            full_text
        )

        debug_logs.append(
            "Multi-agent pipeline completed"
        )

        # -------------------------------
        # EXTRACT PIPELINE OUTPUTS
        # -------------------------------
        risk_analysis = pipeline_output.get(
            "risk_analysis",
            ""
        )

        summary = pipeline_output.get(
            "summary",
            ""
        )

        qa_results = pipeline_output.get(
            "qa_results",
            []
        )
        
        segment_analysis = pipeline_output.get(
            "segment_analysis",
            []
        )

        issues = [risk_analysis]

        debug_logs.append(
            "Summary agent completed"
        )

        debug_logs.append(
            f"QA agent generated {len(qa_results)} results"
        )


        # -------------------------------
        # LANGFUSE TRACE
        # -------------------------------
        with langfuse.start_as_current_observation(
            as_type="span",
            name="Contract Review Pipeline"
        ) as span:

            span.update(
                input={
                    "file_path": file_path,
                    "pages": len(docs),
                    "chunks": len(chunks),
                    "pipeline": "multi_agent_contract_analysis"
                }
            )
            
            span.update(
                output={
                    "summary_generated": bool(summary),
                    "summary_length": len(summary) if summary else 0,
                    "qa_results_count": len(qa_results)
                }
            )

        try:

            langfuse.flush()

        except Exception as e:

            debug_logs.append(
                f"Flush failed: {str(e)}"
            )

        debug_logs.append("TRACE SENT")

    except Exception as e:

        error_msg = str(e)

        trace_error = traceback.format_exc()

        debug_logs.append(error_msg)

        debug_logs.append(trace_error)

        return ContractResponse(
            filename=file_path,
            issues=issues,
            summary=summary,
            qa_results=[],
            segment_analysis=[],
            debug=debug_logs
        )


    db = SessionLocal()

    review = ContractReview(
        filename=file_path,
        summary=summary,
        issues="\n".join(issues)
    )

    db.add(review)
    db.commit()
    db.close()


    return ContractResponse(
        filename=file_path,
        issues=issues,
        summary=summary,
        qa_results=qa_results,
        segment_analysis=segment_analysis,
        debug=debug_logs
    )
