import chromadb
import uuid

# Persistent Chroma DB
client = chromadb.PersistentClient(path="./chroma_db")

collection = client.get_or_create_collection(name="contracts")


def store_chunks(chunks, filename):
    ids = [str(uuid.uuid4()) for _ in chunks]

    collection.upsert(
        documents=chunks,
        ids=ids,
        metadatas=[{"source": filename}] * len(chunks)
    )


def query_chunks(query, n_results=5):
    results = collection.query(
        query_texts=[query],
        n_results=n_results
    )

    docs = results["documents"][0]

    # ✅ REMOVE DUPLICATES (SMART WAY)
    unique_docs = []

    for doc in docs:
        is_duplicate = False

        for existing in unique_docs:
            if doc[:150] == existing[:150]:  # compare first 150 chars
                is_duplicate = True
                break

        if not is_duplicate:
            unique_docs.append(doc)

    return unique_docs
