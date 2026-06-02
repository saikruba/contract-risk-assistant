import chromadb
import uuid
import shutil
import os
from app.core.logger import logger

DB_PATH = "./chroma_db"
COLLECTION_NAME = "contracts"

# -------------------------------
# SINGLETON CLIENT (IMPORTANT FIX)
# -------------------------------
client = chromadb.PersistentClient(path=DB_PATH)


def get_collection():
    return client.get_or_create_collection(name=COLLECTION_NAME)


# -------------------------------
# STORE
# -------------------------------
def store_chunks(chunks, metadatas):
    collection = get_collection()

    ids = [str(uuid.uuid4()) for _ in chunks]

    collection.upsert(
        documents=chunks,
        ids=ids,
        metadatas=metadatas
    )

    logger.info("Stored chunks: %s", len(chunks))
    logger.info("DB COUNT AFTER STORE: %s", collection.count())


# -------------------------------
# QUERY
# -------------------------------
def query_chunks(query, n_results=5):
    collection = get_collection()

    count = collection.count()
    logger.info("DB COUNT BEFORE QUERY: %s", count)

    if count == 0:
        logger.info("⚠️ DB EMPTY %s")
        return []

    results = collection.query(
        query_texts=[query],
        n_results=n_results
    )

    docs = results.get("documents", [[]])[0]
    metas = results.get("metadatas", [[]])[0]

    output = []

    for doc, meta in zip(docs, metas):
        output.append({
            "text": doc,
            "page": meta.get("page", "unknown")
        })

    return output


# -------------------------------
# SAFE RESET (FIXED VERSION)
# -------------------------------
def reset_db():
    global client

    try:
        # 1. Recreate clean persistent client
        client = chromadb.PersistentClient(path=DB_PATH)

        # 2. Delete collection safely
        try:
            client.delete_collection(name=COLLECTION_NAME)
            logger.info("🗑️ Collection deleted %s")
        except Exception as e:
            logger.info("⚠️ Delete skipped (likely doesn't exist): %s", str(e))

        # 3. Recreate fresh collection
        client.get_or_create_collection(name=COLLECTION_NAME)

        logger.info("✅ SAFE RESET SUCCESSFUL %s")

    except Exception as e:
        logger.info("❌ RESET ERROR: %s", str(e))
