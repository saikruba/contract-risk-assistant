from llama_index.core import VectorStoreIndex, Document, Settings
from app.services.vector_service import query_chunks


def qa_agent(query: str, filename: str):
    try:
        # ✅ Check if LLM is configured
        if Settings.llm is None:
            return {
                "answer": "LLM not configured. Please set OPENAI_API_KEY.",
                "sources": []
            }

        chunks = query_chunks(query, filename)

        print(f"[QA] Query: {query}")
        print(f"[QA] Chunks retrieved: {len(chunks)}")

        if not chunks:
            return {
                "answer": "No relevant contract sections found.",
                "sources": []
            }

        # limit context
        chunks = chunks[:8]

        docs = [Document(text=c) for c in chunks]

        index = VectorStoreIndex.from_documents(docs)

        query_engine = index.as_query_engine(response_mode="compact")

        response = query_engine.query(
            f"""
Answer using ONLY the contract.

Question: {query}

- Be clear
- Cite clauses if possible
- If unsure say "Not found in contract"
"""
        )

        return {
            "answer": str(response),
            "sources": chunks
        }

    except Exception as e:
        return {
            "answer": f"Error during QA: {str(e)}",
            "sources": []
        }
