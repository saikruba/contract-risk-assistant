import chromadb
import uuid
import shutil
import os

DB_PATH = "./chroma_db"
COLLECTION_NAME = "contracts"


def get_collection():
    client = chromadb.PersistentClient(path=DB_PATH)
    return client.get_or_create_collection(name=COLLECTION_NAME)


# -------------------------------
# STORE
# -------------------------------
def store_chunks(chunks, filename):
    collection = get_collection()

    ids = [str(uuid.uuid4()) for _ in chunks]

    collection.upsert(
        documents=chunks,
        ids=ids,
        metadatas=[{"source": filename}] * len(chunks)
    )

    print("Stored chunks:", len(chunks))
    print("DB COUNT AFTER STORE:", collection.count())


# -------------------------------
# QUERY
# -------------------------------
def query_chunks(query, n_results=5):
    collection = get_collection()

    count = collection.count()
    print("DB COUNT BEFORE QUERY:", count)

    if count == 0:
        print("⚠️ DB EMPTY")
        return []

    results = collection.query(
        query_texts=[query],
        n_results=n_results
    )

    docs = results["documents"][0]

    unique_docs = []
    for doc in docs:
        if not any(doc[:150] == e[:150] for e in unique_docs):
            unique_docs.append(doc)

    print("RESULT COUNT:", len(unique_docs))
    return unique_docs


# -------------------------------
# RESET (CRITICAL FIX)
# -------------------------------
def reset_db():
    import chromadb

    try:
        client = chromadb.PersistentClient(path="./chroma_db")

        # delete collection safely
        try:
            client.delete_collection(name="contracts")
            print("Collection deleted")
        except Exception as e:
            print("Collection delete error:", e)

        # recreate clean collection
        client.get_or_create_collection(name="contracts")

        print("✅ SAFE RESET SUCCESSFUL")

    except Exception as e:
        print("❌ RESET ERROR:", str(e))
