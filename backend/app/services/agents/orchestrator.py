from app.services.agents.risk_agent import (
    classify_risks
)

from app.services.agents.summary_agent import (
    generate_executive_summary
)


def run_multi_agent_pipeline(contract_text: str):

    # ---------------------------
    # Risk Agent
    # ---------------------------
    risk_analysis = classify_risks(contract_text)

    # ---------------------------
    # Summary Agent
    # ---------------------------
    summary = generate_executive_summary(
        contract_text
    )

    # ---------------------------
    # Empty QA Results
    # ---------------------------
    qa_results = []

    # ---------------------------
    # Final Structured Output
    # ---------------------------
    return {
        "summary": summary,
        "risk_analysis": risk_analysis,
        "qa_results": qa_results
    }
