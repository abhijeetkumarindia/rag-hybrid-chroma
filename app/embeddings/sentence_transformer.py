from langchain_core.embeddings import Embeddings
from sentence_transformers import SentenceTransformer
from app.core.constants import EMBEDDING_MODEL

class SentenceTransformerEmbedding(Embeddings):
  def __init__(self , model_name=EMBEDDING_MODEL):
    self.model=SentenceTransformer(model_name)

  def embed_documents(self , texts):
    return self.model.encode(texts , normalize_embeddings=True).tolist()

  def embed_query(self, text):
    return self.model.encode(text , normalize_embeddings=True).tolist()