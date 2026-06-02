from app.services.vector_service import query_chunks
from app.services.llm_service import call_llama

from app.services.vector_service import query_chunks
from app.services.llm_service import call_llama


def run_qa_agent(
    query: str,
    chat_history=None
):

    history_text = ""

    if chat_history:
        history_text = "\n".join(
            [
                f"User: {item['question']}\nAssistant: {item['answer']}"
                for item in chat_history[-5:]
            ]
        )

    search_query = query

    if history_text:
        search_query = history_text + "\n" + query

    results = query_chunks(
        search_query,
        n_results=8
    )


    if not results:
        return {
            "question": query,
            "answer": "No relevant clauses found.",
            "references": []
        }

    context = "\n\n".join(
        f"Page {r.get('page', 'unknown')}: {r.get('text', '')}"
        for r in results
    )

    prompt = f"""
You are a senior contract review attorney.

Answer ONLY using the provided contract clauses.

Question:
{query}

Contract Clauses:
{context}

Instructions:

1. Answer the user's question directly.
2. Explain the clause in plain English.
3. Highlight any legal, commercial, or operational risks.
4. Mention important limitations or missing protections.
5. If multiple clauses are relevant, summarize them together.
6. Cite the relevant page numbers.
7. If the answer cannot be determined from the contract excerpts, say so clearly.
8. Do not invent facts that are not in the contract.

Response format:

Answer:
<direct answer>

Explanation:
<plain English explanation>

Risk Assessment:
<risk analysis>

Supporting Pages:
<page references>

"""

    answer = call_llama(prompt)

    return {
        "question": query,
        "answer": answer,
        "references": results
    }
