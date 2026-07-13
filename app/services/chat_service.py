from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from app.prompts.retrieval import retrieve_context
from app.prompts.chat import prompt
from app.llm.factory import LLM
llm = LLM.create('groq')

chain = (
    {
        "context":RunnablePassthrough() | retrieve_context,
        "query":RunnablePassthrough(),
    } | prompt | llm |  StrOutputParser()
)


async def stream_chat(query: str):
    async for chunk in chain.astream(query):
        yield str(chunk)