from .base import BaseEmbedding

class SentenceTransformerEmbedding(BaseEmbedding):
    def embed(self, text):
        return 'embeding '