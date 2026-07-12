
from .base import BaseEmbedding

class GeminiEmbedding(BaseEmbedding):
    def embed(self, text):
        return text 