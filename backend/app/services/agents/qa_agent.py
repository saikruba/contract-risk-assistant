from app.services.vector_service import query_chunks
from app.services.llm_service import call_llama


def simple_rerank(query: str, results: list):
    query_terms = set(query.lower().split())

    def score(doc):
        text = doc.get("text", "").lower()
        return sum(1 for w in query_terms if w in text)

    return sorted(results, key=score, reverse=True)


def run_qa_agent(
    query: str,
    chat_history=None
):

    history_text = ""
    

    if chat_history:
        history_text = "\n".join(
            [
                f"User: {item['question']}\nAssistant: {item['answer']}"
                for item in chat_history[-3:]
            ]
        )

    search_query = query

    
    sub_queries = [
        search_query,
        "termination clause",
        "liability limitation",
        "indemnification",
        "payment terms"
    ]
    
    results = []
    
    for q in sub_queries:
        results.extend(query_chunks(q, n_results=3))

# -------------------------------
# DEDUPLICATION (IMPORTANT)
# -------------------------------
    seen = set()
    deduped = []

    for r in results:
        key = (r.get("page"), r.get("text")[:200])
        if key not in seen:
            seen.add(key)
            deduped.append(r)

    results = deduped

# -------------------------------
# RERANK + TOP-K FILTER
# -------------------------------
    results = simple_rerank(query, results)[:3]

    if not results:
        return {
            "question": query,
            "answer": "No relevant clauses found.",
            "references": []
        }

    context = "\n\n".join(
        f"Page {r.get('page', 'unknown')}: {r.get('text', '')[:500]}"
        for r in results
    )

    prompt = f"""
You are a senior contract review attorney and AI legal assistant.

Your job is to answer user questions strictly using the provided contract clauses.

---------------------------
CONTRACT CONTEXT
---------------------------
{context}

---------------------------
QUESTION
---------------------------
{query}

---------------------------
CHAT CONTEXT (if any)
---------------------------
{history_text}

---------------------------
INSTRUCTIONS
---------------------------

- Answer the question directly and clearly in a conversational tone.
- Do NOT use headings like "Answer:", "Explanation:", or "Risk Assessment:".
- Do NOT format like a report.
- Explain clauses naturally in 1–2 short paragraphs.
- Mention key legal risks ONLY if they are important.
- If multiple clauses apply, merge them into one clear explanation.
- Always stay strictly within the provided contract context.
- If the answer is not in the contract, clearly say it is not found.
- Always include relevant page reference(s) at the end in a simple form like: (Page 6).
- Keep responses concise and to the point.
- Do not hallucinate

"""

    answer = call_llama(prompt, max_tokens=500)

    return {
        "question": query,
        "answer": answer,
        "references": results
    }
