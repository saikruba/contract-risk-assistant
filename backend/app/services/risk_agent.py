from app.services.llm_service import call_llama


def classify_risks(contract_text: str):

    prompt = f"""
You are an expert legal contract risk analysis assistant.

Your task is to analyze the contract and identify legal,
financial, operational, and compliance risks.

Analyze the contract for the following risk categories:

1. Termination Risk
2. Limitation of Liability Risk
3. Indemnification Risk
4. Payment & Financial Risk
5. Confidentiality & Data Protection Risk
6. Intellectual Property (IP) Ownership Risk
7. Governing Law & Jurisdiction Risk
8. Auto-Renewal & Renewal Notice Risk
9. Non-Compete / Non-Solicitation Risk
10. Warranty & Disclaimer Risk
11. Compliance & Regulatory Risk
12. SLA / Performance Risk
13. Assignment & Subcontracting Risk
14. Force Majeure Risk
15. Amendment / Change Control Risk

Instructions:

- Identify ONLY risks actually present in the contract
- Do NOT hallucinate or invent clauses
- If a category is not found, say:
  "No relevant clause detected"
- Explain risks in simple business English
- Keep explanations concise but informative
- Mention clause excerpts where possible
- Mention page or section references if available
- Detect one-sided or overly broad clauses
- Detect uncapped liability exposure
- Detect broad indemnification obligations
- Detect vague payment obligations
- Detect silent auto-renewal clauses
- Detect perpetual confidentiality obligations
- Detect IP transfer or ownership ambiguity

For each detected risk provide:

- Risk Category
- Severity:
    LOW
    MEDIUM
    HIGH
    CRITICAL
- Clause Excerpt
- Risk Explanation
- Business Impact
- Page/Section Reference
- Suggested Mitigation

After analysis provide:

1. Overall Risk Score (1-10)
2. Overall Risk Level:
    LOW
    MEDIUM
    HIGH
    CRITICAL

3. Executive Summary:
- Top major risks
- Most dangerous clauses
- Missing protections
- Key negotiation priorities

Return the response in clean structured bullet points.

Contract:
{contract_text[:12000]}
"""

    response = call_llama(prompt)

    return response
