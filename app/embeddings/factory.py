from .gemini import GeminiEmbedding
from .sentence_transformer import SentenceTransformerEmbedding
from app.core.constants import EMBEDDING_MODEL


class EmbeddingFactory:
    @staticmethod
    def create(provider: str, model_name: str | None = None):
        if provider == 'gemini':
            return GeminiEmbedding()
        if provider == 'sentence-transformer':
            if model_name is None:
                model_name = EMBEDDING_MODEL
            return SentenceTransformerEmbedding(model_name)
        raise ValueError("unknown embedding provided")