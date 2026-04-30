import chromadb
import uuid
from sentence_transformers import SentenceTransformer

model = SentenceTransformer("all-MiniLM-L6-v2")

client = chromadb.PersistentClient(path="./chroma_db")
collection = client.get_or_create_collection(name="contracts")


def store_chunks(chunks, filename):
    embeddings = model.encode(chunks).tolist()

    ids = [str(uuid.uuid4()) for _ in chunks]

    metadatas = [
        {"source": filename, "chunk_id": i}
        for i in range(len(chunks))
    ]

    collection.upsert(
        documents=chunks,
        embeddings=embeddings,
        ids=ids,
        metadatas=metadatas
    )


def query_chunks(query, filename=None, n_results=5):
    query_embedding = model.encode([query]).tolist()

    results = collection.query(
        query_embeddings=query_embedding,
        n_results=n_results,
        where={"source": filename} if filename else None
    )

    docs = results.get("documents", [[]])[0]

    # remove duplicates
    seen = set()
    unique_docs = []

    for doc in docs:
        key = doc[:200]
        if key not in seen:
            seen.add(key)
            unique_docs.append(doc)

    return unique_docs
