from app.services.llm_service import call_llama

from langfuse import get_client

langfuse = get_client()

def generate_executive_summary(contract_text: str):

    prompt = f"""
You are an executive legal summarization assistant.

Create a concise executive summary of this contract.

Include:
- Contract purpose
- Key business obligations
- Important payment terms
- Termination conditions
- Major legal risks
- Key negotiation concerns

Use simple business English.
Keep it concise and readable.

Contract:
{contract_text[:10000]}
"""
    with langfuse.start_as_current_observation(
        as_type="generation",
        name="Executive Summary"
    ):
        summary = call_llama(prompt)

    return summary
