import re
from app.embeddings.factory import EmbeddingFactory
from app.core.constants import EMBEDDING_MODEL, DB_PATH, PDF_DIRECTORY
from app.ingestion.loaders import load_doc
from app.ingestion.chunkers.index import chunk_documents
from langchain_chroma import Chroma
from rank_bm25 import BM25Okapi
from langchain_core.documents import Document
from pathlib import Path
import logging

BASE_DIRECTORY = Path(__file__).resolve().parent.parent
TRACKING_FILE = BASE_DIRECTORY/'monitoring'/'tracing.json'
logging.basicConfig(
   filename=str(TRACKING_FILE),
   level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    force=True
)
def tokenizer(text):
  return re.findall(r'\w+', text.lower())

def reciprocal_rank_fusion(result_list , k=60):
  scores ={}
  lookup={}
  for results in result_list:
    for rank , doc in enumerate(results):
      key= doc.page_content
      lookup[key] = doc
      scores[key] = scores.get(key,0)+1 /(k+rank+1)
  ranked = sorted(scores.items() , key=lambda x:x[1] , reverse=True)
  return [lookup[k] for k , _ in ranked]


def building_indexes():
    logging.info("Retrieving vector database ")
    embeddings = EmbeddingFactory.create(
        "sentence-transformer",
        EMBEDDING_MODEL
    )
    vector_store = Chroma(
        persist_directory=DB_PATH,
        embedding_function=embeddings
    )

    if vector_store._collection.count() == 0:
        logging.error("Vector database is empty")
        raise ValueError("Vector database is empty.")
    data = vector_store.get(include=["documents", "metadatas"])
    logging.info("Chunks fetched")
    chunks = [
        Document(page_content=doc, metadata=meta)
        for doc, meta in zip(data["documents"], data["metadatas"])
    ]
    logging.info("Corpus ready")
    corpus = [doc.page_content for doc in chunks]

    if not corpus:
        logging.error("No chunks found in the vector database")
        raise ValueError("No chunks found in the vector database.")

    bm25 = BM25Okapi([tokenizer(text) for text in corpus])

    print(f"Loaded {len(chunks)} chunks from Chroma.")
    logging.info(f"Loaded {len(chunks)} chunks from Chroma.")
    return vector_store, bm25, chunks


def initial_indexes(pdf_path=PDF_DIRECTORY):
    docs = load_doc(pdf_path)
    chunks = chunk_documents(docs)
    print(" Total chunks:", len(chunks))

    if len(chunks) == 0:
        raise ValueError("No document chunks found to index.")

    embeddings = EmbeddingFactory.create('sentence-transformer', EMBEDDING_MODEL)
    vector_store = Chroma(
        persist_directory=DB_PATH,
        embedding_function=embeddings,
    )
    try:
        current_count = vector_store._collection.count()
    except Exception:
        current_count = 0

    if current_count == 0:
        print("Creating new vector database...")
        vector_store.add_documents(chunks)
        try:
            current_count = vector_store._collection.count()
        except Exception:
            current_count = len(chunks)

    return current_count

