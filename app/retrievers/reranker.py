from app.core.constants import RE_RANKING_MODEL, FINAL_TOP_K
from sentence_transformers import CrossEncoder


def rerank(query, docs):
    reranker = CrossEncoder(RE_RANKING_MODEL)
    pairs = [[query, d.page_content] for d in docs]
    scores = reranker.predict(pairs)

    ranked = sorted(zip(scores, docs), key=lambda x: x[0], reverse=True)
    return [doc for _, doc in ranked[:FINAL_TOP_K]]
