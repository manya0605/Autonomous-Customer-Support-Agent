import os
import json
import faiss

from sentence_transformers import SentenceTransformer


# ============================================================
# PATHS
# ============================================================

BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.dirname(
            os.path.dirname(os.path.abspath(__file__))
        )
    )
)

KNOWLEDGE_BASE_DIR = os.path.join(
    BASE_DIR,
    "knowledge_base"
)

VECTOR_DIR = os.path.join(
    BASE_DIR,
    "vector_store"
)

INDEX_PATH = os.path.join(
    VECTOR_DIR,
    "knowledge.index"
)

METADATA_PATH = os.path.join(
    VECTOR_DIR,
    "metadata.json"
)


# ============================================================
# EMBEDDING MODEL
# ============================================================

MODEL_NAME = "all-MiniLM-L6-v2"

print("Loading embedding model...")

embedding_model = SentenceTransformer(
    MODEL_NAME
)

print("Embedding model loaded.")


# ============================================================
# DOCUMENT LOADING
# ============================================================

def load_documents():

    documents = []

    if not os.path.exists(KNOWLEDGE_BASE_DIR):
        raise ValueError(
            "Knowledge base directory does not exist."
        )

    for filename in os.listdir(KNOWLEDGE_BASE_DIR):

        if not filename.endswith(".txt"):
            continue

        file_path = os.path.join(
            KNOWLEDGE_BASE_DIR,
            filename
        )

        with open(
            file_path,
            "r",
            encoding="utf-8"
        ) as file:

            text = file.read()

        documents.append(
            {
                "source": filename,
                "text": text
            }
        )

    return documents


# ============================================================
# TEXT CHUNKING
# ============================================================

def chunk_text(
    text,
    chunk_size=700,
    overlap=100
):

    words = text.split()

    chunks = []

    start = 0

    while start < len(words):

        end = start + chunk_size

        chunk = " ".join(
            words[start:end]
        )

        if chunk.strip():

            chunks.append(chunk)

        start += chunk_size - overlap

    return chunks


# ============================================================
# BUILD VECTOR DATABASE
# ============================================================

def build_index():

    os.makedirs(
        VECTOR_DIR,
        exist_ok=True
    )

    documents = load_documents()

    chunks = []

    metadata = []

    for document in documents:

        document_chunks = chunk_text(
            document["text"]
        )

        for chunk_number, chunk in enumerate(
            document_chunks,
            start=1
        ):

            chunks.append(chunk)

            metadata.append(
                {
                    "source": document["source"],
                    "chunk_id": chunk_number,
                    "text": chunk
                }
            )

    if not chunks:

        raise ValueError(
            "No documents found in knowledge_base."
        )

    print(
        f"Creating embeddings for {len(chunks)} chunks..."
    )

    embeddings = embedding_model.encode(
        chunks,
        convert_to_numpy=True,
        normalize_embeddings=True
    )

    dimension = embeddings.shape[1]

    index = faiss.IndexFlatIP(
        dimension
    )

    index.add(
        embeddings
    )

    faiss.write_index(
        index,
        INDEX_PATH
    )

    with open(
        METADATA_PATH,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            metadata,
            file,
            indent=2,
            ensure_ascii=False
        )

    print(
        f"Vector index created with {len(chunks)} chunks."
    )


# ============================================================
# LOAD VECTOR DATABASE
# ============================================================

def load_index():

    if not os.path.exists(INDEX_PATH):

        build_index()

    if not os.path.exists(METADATA_PATH):

        build_index()

    index = faiss.read_index(
        INDEX_PATH
    )

    with open(
        METADATA_PATH,
        "r",
        encoding="utf-8"
    ) as file:

        metadata = json.load(file)

    return index, metadata


# ============================================================
# SEARCH KNOWLEDGE BASE
# ============================================================

def search_knowledge(
    query,
    top_k=3,
    score_threshold=0.50
):

    index, metadata = load_index()

    query_embedding = embedding_model.encode(
        [query],
        convert_to_numpy=True,
        normalize_embeddings=True
    )

    scores, indices = index.search(
        query_embedding,
        top_k
    )

    results = []

    for score, index_id in zip(
        scores[0],
        indices[0]
    ):

        if index_id == -1:
            continue

        score = float(score)

        # ----------------------------------------------------
        # Ignore weak / irrelevant matches
        # ----------------------------------------------------

        if score < score_threshold:
            continue

        item = metadata[index_id]

        results.append(
            {
                "score": score,
                "source": item.get(
                    "source",
                    "Unknown source"
                ),
                "chunk_id": item.get(
                    "chunk_id"
                ),
                "text": item.get(
                    "text",
                    ""
                )
            }
        )

    return results


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    build_index()

    results = search_knowledge(
        "Can I get a refund for a delayed order?"
    )

    for result in results:

        print("\nSOURCE:")
        print(result["source"])

        print("\nCHUNK:")
        print(result["chunk_id"])

        print("\nSCORE:")
        print(result["score"])

        print("\nCONTENT:")
        print(result["text"])

        print("-" * 60)