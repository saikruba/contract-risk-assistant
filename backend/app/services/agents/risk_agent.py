from app.services.llm_service import call_llama


def classify_risks(contract_text: str):

    prompt = f"""
You are a senior commercial contracts attorney.

TASK

Perform a COMPLETE CONTRACT RISK SWEEP.

Review the contract against a predefined legal risk checklist.

Analyze ONLY clauses that actually exist in the contract.

Do NOT hallucinate.
Do NOT invent clauses.
Do NOT assume risks that are not supported by contract language.

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

4. Why the clause may create legal or business risk

====================================================
RISK CATEGORIES
====================================================

1. Indemnification Obligations

Check for:
- One-sided indemnities
- Broad indemnification language
- Third-party claims
- Defense obligations

2. Limitation of Liability

Check for:
- Liability caps
- No liability cap
- Unlimited liability
- Excluded damages

3. Termination Rights

Check for:
- Convenience termination
- Termination for cause
- Immediate termination rights
- One-sided termination rights

4. Notice Periods

Check for:
- Termination notice periods
- Renewal notice periods
- Short notice requirements

5. Auto-Renewal

Check for:
- Automatic renewal
- Evergreen clauses
- Renewal opt-out obligations

6. Intellectual Property Ownership

Check for:
- Ownership transfer
- Work-product ownership
- Licensing provisions
- IP ambiguity

7. Governing Law & Jurisdiction

Check for:
- Governing law
- Court selection
- Venue requirements
- Foreign jurisdiction risk

8. Confidentiality

Check for:
- Confidentiality obligations
- Duration of confidentiality
- Perpetual confidentiality
- Data protection obligations

9. Payment Terms & Penalties

Check for:
- Payment deadlines
- Late fees
- Interest penalties
- Ambiguous payment obligations

10. Dispute Resolution

Check for:
- Arbitration
- Litigation
- Mediation
- Class-action waiver

====================================================
RISK SCORING GUIDELINES
====================================================

Assign HIGH risk when:

- Liability is uncapped
- Broad indemnification exists
- IP ownership is transferred away
- Auto-renewal occurs without notice
- Confidentiality is perpetual
- Foreign jurisdiction creates material burden
- Termination rights are one-sided
- Payment obligations are vague
- Arbitration significantly limits remedies

Assign MEDIUM risk when:

- Clause exists but is imbalanced
- Liability cap is unusually high
- Notice periods are short
- Language is ambiguous

Assign LOW risk when:

- Clause is balanced
- Market-standard protections exist
- Risk exposure is limited

====================================================
OUTPUT FORMAT
====================================================

STRUCTURED RISK REGISTER

| Risk Category | Found (Yes/No) | Risk Rating | Plain English Summary | Business Impact |

Provide exactly one row for each category.

====================================================
AFTER THE TABLE
====================================================

TOP RISKS

List the 3 most significant risks.

----------------------------------------------------

MISSING PROTECTIONS

List important protections that appear absent.

----------------------------------------------------

NEGOTIATION PRIORITIES

List the clauses that should be negotiated first.

----------------------------------------------------

OVERALL RISK SCORE

Provide a score from 1 to 10.

----------------------------------------------------

OVERALL RISK LEVEL

Return ONLY ONE:

LOW
MEDIUM
HIGH

====================================================
CONTRACT
====================================================

{contract_text[:15000]}
"""

    response = call_llama(prompt)

    return response
