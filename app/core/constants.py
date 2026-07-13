import os

EMBEDDING_MODEL='sentence-transformers/all-MiniLM-L6-v2'
RE_RANKING_MODEL='cross-encoder/ms-marco-MiniLM-L-6-v2'
CHUNK_SIZE=400
CHUNK_OVERLAP=150
VECTOR_TOP_K=10
BM25_TOP_K=10
FINAL_TOP_K=10

PDF_DIRECTORY=os.path.join(os.getcwd(), "uploads")
INDEX_NAME='resume-rag'

NOTE_BOOK_PATH = os.getcwd()
DB_PATH = os.path.join(NOTE_BOOK_PATH, "website_chroma_db")

import logging

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# Don't raise on import — allow the application to start without these keys.
# Components that require these keys should check and raise or disable features as appropriate.
if not GROQ_API_KEY:
    logging.warning("GROQ_API_KEY not set; GROQ-dependent features will be disabled.")

if not GOOGLE_API_KEY:
    logging.warning("GOOGLE_API_KEY not set; Google-dependent features will be disabled.")