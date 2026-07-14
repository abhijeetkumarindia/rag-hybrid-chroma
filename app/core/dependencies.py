import os
import logging
import re
from functools import lru_cache
from pathlib import Path

from langchain_chroma import Chroma
from langchain_core.documents import Document
from rank_bm25 import BM25Okapi

from app.core.constants import DB_PATH, EMBEDDING_MODEL, PDF_DIRECTORY
from app.embeddings.factory import EmbeddingFactory
from app.ingestion.chunkers.index import chunk_documents
from app.ingestion.loaders import load_doc

BASE_DIRECTORY = Path(__file__).resolve().parent.parent
TRACKING_FILE = BASE_DIRECTORY / "monitoring" / "tracing.json"

logging.basicConfig(
    filename=str(TRACKING_FILE),
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    force=True,
)


def tokenizer(text):
    return re.findall(r"\w+", text.lower())


def reciprocal_rank_fusion(result_list, k=60):
    scores = {}
    lookup = {}

    for results in result_list:
        for rank, doc in enumerate(results):
            key = (
                doc.page_content,
                doc.metadata.get("source"),
                doc.metadata.get("page"),
            )

            lookup[key] = doc
            scores[key] = scores.get(key, 0) + 1 / (k + rank + 1)

    ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)

    return [lookup[key] for key, _ in ranked]


@lru_cache(maxsize=1)
def get_embeddings():
    return EmbeddingFactory.create(
        "sentence-transformer",
        EMBEDDING_MODEL
    )

@lru_cache(maxsize=1)
def building_indexes():
    """
    Load the vector database and build the BM25 index once.
    The result is cached and reused for subsequent requests.
    """

    logging.info("Loading vector database...")

    embeddings = get_embeddings()

    vector_store = Chroma(
        persist_directory=DB_PATH,
        embedding_function=embeddings,
    )

    if vector_store._collection.count() == 0:
        logging.error("Vector database is empty.")
        raise ValueError("Vector database is empty.")

    data = vector_store.get(include=["documents", "metadatas"])

    chunks = [
        Document(page_content=doc, metadata=meta)
        for doc, meta in zip(data["documents"], data["metadatas"])
    ]

    if not chunks:
        logging.error("No chunks found.")
        raise ValueError("No chunks found.")

    corpus = [doc.page_content for doc in chunks]

    bm25 = BM25Okapi(
        [tokenizer(text) for text in corpus]
    )

    logging.info(
        "Loaded %d chunks from Chroma.",
        len(chunks),
    )

    return vector_store, bm25, chunks


def initial_indexes(pdf_path=PDF_DIRECTORY):
    docs = load_doc(pdf_path)
    chunks = chunk_documents(docs)
    
    if not chunks:
        raise ValueError("No document chunks found to index.")

    embeddings = EmbeddingFactory.create(
        "sentence-transformer",
        EMBEDDING_MODEL,
    )

    vector_store = Chroma(
        persist_directory=DB_PATH,
        embedding_function=embeddings,
    )

    try:
        current_count = vector_store._collection.count()
    except Exception:
        current_count = 0

    if current_count == 0:
        logging.info("Creating new vector database...")
        vector_store.add_documents(chunks)

        try:
            current_count = vector_store._collection.count()
        except Exception:
            current_count = len(chunks)

    # IMPORTANT:
    # If the vector database changes,
    # clear the cached BM25/vector store.
    building_indexes.cache_clear()

    logging.info(
        "Vector database contains %d chunks.",
        current_count,
    )

    return current_count