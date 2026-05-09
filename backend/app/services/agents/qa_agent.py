from app.services.vector_service import query_chunks
from app.services.llm_service import call_llama


def run_qa_agent(query: str):

    results = query_chunks(query)

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
You are a legal contract assistant.

Answer the question using ONLY the provided clauses.

Question:
{query}

Contract Clauses:
{context}

Instructions:
- Give a direct plain-English answer
- Mention page references
- Do not hallucinate
"""

    answer = call_llama(prompt)

    return {
        "question": query,
        "answer": answer,
        "references": results
    }
