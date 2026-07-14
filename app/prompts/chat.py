from langchain_core.prompts import ChatPromptTemplate

prompt = ChatPromptTemplate.from_template("""
  You are an enterprise AI assistant.
Instructions:
1. Answer ONLY using provided context with better polished sentence.
2. Use markdown headings and bullet points.
3. Highlight keywords in **bold**.
4. If answer unavailable, say: I do not know.
5. Answer briefly. Omit unnecessary details.

Context:
{context}
Question:
{query}

  """)
