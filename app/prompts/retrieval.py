from app.retrievers.hybrid import hybrid_search 
from app.retrievers.reranker import rerank 
def retrieve_context(query):
    docs = hybrid_search(query)
    docs = rerank(query , docs)
    return '\n\n'.join(doc.page_content for doc in docs)

    