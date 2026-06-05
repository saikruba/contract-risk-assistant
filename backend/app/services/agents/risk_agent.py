from app.services.llm_service import call_llama

from langfuse import get_client

langfuse = get_client()

def classify_risks(contract_text: str):

    prompt = f"""
You are a senior commercial contracts attorney specializing in
contract risk assessment and legal review.

====================================================
TASK
====================================================

Perform a COMPLETE CONTRACT RISK SWEEP.

Review the contract against a predefined legal risk checklist.

Analyze ONLY clauses that actually exist in the contract.

Do NOT hallucinate.
Do NOT invent clauses.
Do NOT assume risks not supported by contract language.

The same contract should produce substantially the same
risk assessment on repeated reviews.

Use the scoring framework consistently.

====================================================
RISK ASSESSMENT FRAMEWORK
====================================================

For each category determine:

1. Whether the clause exists
2. What the clause says in plain English
3. Risk rating:
   LOW
   MEDIUM
   HIGH
4. Why the clause creates legal or business risk

====================================================
RISK CATEGORIES
====================================================

1. Indemnification Obligations

Check for:
- One-sided indemnities
- Broad indemnification language
- Third-party claims
- Defense obligations

----------------------------------------------------

2. Limitation of Liability

Check for:
- Liability caps
- No liability cap
- Unlimited liability
- Excluded damages

----------------------------------------------------

3. Termination Rights

Check for:
- Convenience termination
- Termination for cause
- Immediate termination rights
- One-sided termination rights

----------------------------------------------------

4. Notice Periods

Check for:
- Termination notice periods
- Renewal notice periods
- Short notice requirements

----------------------------------------------------

5. Auto-Renewal

Check for:
- Automatic renewal
- Evergreen clauses
- Renewal opt-out obligations

----------------------------------------------------

6. Intellectual Property Ownership

Check for:
- Ownership transfer
- Work-product ownership
- Licensing provisions
- IP ambiguity

----------------------------------------------------

7. Governing Law & Jurisdiction

Check for:
- Governing law
- Court selection
- Venue requirements
- Foreign jurisdiction risk

----------------------------------------------------

8. Confidentiality

Check for:
- Confidentiality obligations
- Duration of confidentiality
- Perpetual confidentiality
- Data protection obligations

----------------------------------------------------

9. Payment Terms & Penalties

Check for:
- Payment deadlines
- Late fees
- Interest penalties
- Ambiguous payment obligations

----------------------------------------------------

10. Dispute Resolution

Check for:
- Arbitration
- Litigation
- Mediation
- Class-action waiver

====================================================
RISK SCORING GUIDELINES
====================================================

Assign HIGH risk when ANY of the following are present:

- Unlimited liability
- No liability cap
- Broad indemnification obligations
- Perpetual confidentiality obligations
- Automatic renewal without notice
- Exclusive foreign jurisdiction
- IP ownership transferred away from customer
- One-sided termination rights
- Mandatory arbitration significantly limiting remedies
- Vague or undefined payment obligations

----------------------------------------------------

Assign MEDIUM risk when:

- Clause exists but is imbalanced
- Liability cap is unusually high
- Notice periods are short
- Language is ambiguous
- Protections are incomplete

----------------------------------------------------

Assign LOW risk when:

- Clause is balanced
- Risk exposure is limited
- Market-standard protections exist

====================================================
MANDATORY RULES
====================================================

Every category MUST appear in the final report.

If a category is not found:

Found = No

Risk Rating = LOW

Clause Evidence = No relevant clause detected

Plain English Summary = No relevant clause detected

Business Impact = Minimal risk due to absence of clause

====================================================
OUTPUT FORMAT
====================================================

STRUCTURED RISK REGISTER

| Risk Category | Found | Risk Rating | Clause Evidence | Summary | Business Impact |

Provide exactly one row for each category.

====================================================
AFTER THE TABLE
====================================================

RISK DISTRIBUTION

High Risk Categories: X

Medium Risk Categories: X

Low Risk Categories: X

----------------------------------------------------

TOP RISKS

List the 3 most significant risks.

----------------------------------------------------

MISSING PROTECTIONS

List important protections that appear absent.

----------------------------------------------------

NEGOTIATION PRIORITIES

List the clauses that should be negotiated first.

----------------------------------------------------

EXECUTIVE SUMMARY

Provide:

- Contract Purpose
- Overall Risk Posture
- Key Risk Drivers
- Most Important Negotiation Points

Maximum 5 bullet points.

====================================================
OVERALL RISK SCORING METHODOLOGY
====================================================

Assign points:

LOW = 1
MEDIUM = 2
HIGH = 3

Calculate the total score using all 10 categories.

Score Range:

1-12 = LOW

13-20 = MEDIUM

21-30 = HIGH

You MUST calculate the score using the category ratings.

Do NOT estimate.

====================================================
FINAL OUTPUT
====================================================

OVERALL RISK SCORE: X/30

OVERALL RISK LEVEL: LOW

OR

OVERALL RISK LEVEL: MEDIUM

OR

OVERALL RISK LEVEL: HIGH

====================================================
CONTRACT
====================================================

{contract_text[:15000]}
"""

    with langfuse.start_as_current_observation(
        as_type="span",
        name="Risk Assessment"
    ):

        response = call_llama(prompt)

    return response
