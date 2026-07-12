from .gemini import GeminiEmbedding
from .sentence_transformer import SentenceTransformerEmbedding

class EmbeddingFactory:
    @staticmethod
    def create(provider:str):
        if provider == 'gemini':
            return GeminiEmbedding()
        if provider == 'sentence-transformer':
            return SentenceTransformerEmbedding()
        raise ValueError("unknown embedding provided ")