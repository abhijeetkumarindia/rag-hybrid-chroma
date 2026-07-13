from .base import BaseLLM


class LLM(BaseLLM):
    @staticmethod
    def create(provided):
        if provided == 'gemini':
            from .gemini import get_chat_google_generative_ai
            return get_chat_google_generative_ai()
        if provided == 'groq':
            from .groq import get_chat_groq_llm
            return get_chat_groq_llm()
        raise ValueError(f"Unsupported LLM provider: {provided}")
