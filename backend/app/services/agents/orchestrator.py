from app.services.agents.risk_agent import classify_risks
from app.services.agents.summary_agent import generate_executive_summary


def run_multi_agent_pipeline(contract_text: str):

    # 1. Risk agent
    risk_output = classify_risks(contract_text)

    segment_analysis = risk_output["segment_analysis"]
    avg_score = risk_output["avg_score"]
    overall_level = risk_output["overall_level"]
    risk_report = risk_output["risk_report"]

    # 2. Summary agent
    summary = generate_executive_summary(
        segment_analysis,
        avg_score,
        overall_level
    )

    # 3. Final output
# 3. Final output
    return {
        "risk_analysis": risk_report,
        "summary": summary,
        "segment_analysis": segment_analysis,
        "avg_score": avg_score,
        "overall_level": overall_level,
        "qa_results": []
    }
