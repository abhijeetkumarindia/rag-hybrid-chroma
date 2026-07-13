import os
from langchain_google_genai import ChatGoogleGenerativeAI


def get_chat_google_generative_ai():
    api_key = os.getenv('GOOGLE_API_KEY') or os.getenv('GEMINI_API_KEY')
    if not api_key:
        raise ValueError('GOOGLE_API_KEY or GEMINI_API_KEY must be set to use the Gemini LLM')

    return ChatGoogleGenerativeAI(
        model='gemini-2.5-flash',
        temperature=0.2,
        api_key=api_key,
    )