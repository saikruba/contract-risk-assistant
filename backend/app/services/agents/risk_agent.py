import re
import json

from app.services.llm_service import call_llama
from langfuse import get_client

langfuse = get_client()

SEVERITY_REFERENCE = {
    "HIGH": 3,
    "MEDIUM": 2,
    "LOW": 1
}


def split_contract_into_segments(contract_text):

    pattern = r"(?m)^\d+\."

    matches = list(
        re.finditer(pattern, contract_text)
    )

    if not matches:
        return [contract_text]

    segments = []

    start = 0

    for match in matches:

        end = match.start()

        if end > start:
            segments.append(
                contract_text[start:end].strip()
            )

        start = end

    segments.append(
        contract_text[start:].strip()
    )

    return [
        s for s in segments
        if s.strip()
    ]


def analyze_segment(segment):

    prompt = f"""
You are a senior contracts attorney.

Analyze ONLY this contract segment.

SEGMENT

{segment}

Instructions:

- Extract all legal clauses.
- Multiple clauses may exist.
- Do not invent clauses.
- Assign HIGH, MEDIUM or LOW severity.
- Return one JSON object per clause.
- Return [] if none exist.

Return STRICT JSON:

[
{{
"clause_name":"...",
"clause_excerpt":"...",
"severity":"HIGH",
"reason":"..."
}}
]

Return [] if nothing relevant is found.
"""

    response = call_llama(prompt)

    try:

        response = response.strip()

        if response.startswith("```json"):
            response = response.replace(
                "```json",
                ""
            )

        if response.endswith("```"):
            response = response[:-3]

        response = response.strip()

        return json.loads(response)

    except Exception:

        return []


def classify_risks(contract_text: str):

    # --------------------------
    # Split contract
    # --------------------------
    segments = split_contract_into_segments(
        contract_text
    )

    # limit to first 15 segments
    segments = segments[:15]

    SEGMENT_WISE_ANALYSIS = []

    # --------------------------
    # Segment-wise analysis
    # --------------------------
    for segment in segments:

        result = analyze_segment(segment)

        SEGMENT_WISE_ANALYSIS.extend(result)

    # --------------------------
    # No clauses found
    # --------------------------
    if not SEGMENT_WISE_ANALYSIS:

        return {
            "risk_report": """
STRUCTURED RISK REGISTER

No significant legal risks detected.

OVERALL RISK SCORE: 0

OVERALL RISK LEVEL: LOW
""",
            "summary": """
- Contract purpose could not be determined.
- No material clauses identified.
- Overall risk posture is low.
"""
        }

    # --------------------------
    # Score calculation
    # --------------------------
    total_risk_score = 0

    high_count = 0
    medium_count = 0
    low_count = 0

    for item in SEGMENT_WISE_ANALYSIS:

        severity = item.get(
            "severity",
            "LOW"
        ).upper()

        score = SEVERITY_REFERENCE.get(
            severity,
            1
        )

        item["score"] = score

        total_risk_score += score

        if severity == "HIGH":
            high_count += 1

        elif severity == "MEDIUM":
            medium_count += 1

        else:
            low_count += 1

    # --------------------------
    # Normalize score
    # --------------------------
    num_clauses = len(
        SEGMENT_WISE_ANALYSIS
    )

    avg_score = total_risk_score / max(
        num_clauses,
        1
    )

    # --------------------------
    # Overall risk level
    # --------------------------
    if avg_score < 1.5:

        overall_level = "LOW"

    elif avg_score < 2.5:

        overall_level = "MEDIUM"

    else:

        overall_level = "HIGH"
        
        

    # ==================================================
    # BUILD RISK REPORT IN PYTHON
    # ==================================================
    risk_report = """
STRUCTURED RISK REGISTER

"""

    for item in SEGMENT_WISE_ANALYSIS:

        risk_report += f"""
----------------------------------------
Risk Category : {item.get("clause_name","")}

Risk Rating   : {item.get("severity","")}

Score         : {item.get("score",1)}

Evidence      : {item.get("clause_excerpt","")}

Reason        : {item.get("reason","")}

"""

    risk_report += f"""

========================================

RISK DISTRIBUTION

High Risk Categories   : {high_count}

Medium Risk Categories : {medium_count}

Low Risk Categories    : {low_count}

========================================

OVERALL RISK SCORE : {avg_score:.2f}

OVERALL RISK LEVEL : {overall_level}
"""



    return {
        "risk_report": risk_report,
        "segment_analysis": SEGMENT_WISE_ANALYSIS,
        "avg_score": avg_score,
        "overall_level": overall_level
    }
