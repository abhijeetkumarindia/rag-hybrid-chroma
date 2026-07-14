from langchain_groq import ChatGroq


def get_chat_groq_llm():
    return ChatGroq(
        model='llama-3.3-70b-versatile',
        temperature=0.2,
        api_key='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',
    )
