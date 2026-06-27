from app.services.llm_service import call_llama
from langfuse import get_client
import json

langfuse = get_client()


def generate_executive_summary(
    segment_analysis,
    avg_score,
    overall_level
) -> str:

    prompt = f"""
You are a senior legal executive assistant.

Segment-wise contract analysis has already been completed.

Use ONLY the supplied clause findings.

Do not invent clauses.

CLAUSE FINDINGS

{json.dumps(segment_analysis[:50], indent=2)}

OVERALL RISK SCORE

{avg_score:.2f}

OVERALL RISK LEVEL

{overall_level}

Provide a concise executive summary.

Include:

- Contract Purpose
- Overall Risk Posture
- Key Risk Drivers
- Most Important Negotiation Points
- Missing Protections (if any)


Use clear business English.
"""

    with langfuse.start_as_current_observation(
        as_type="generation",
        name="Executive Summary"
    ):
        summary = call_llama(prompt)

    return summary
