import logging

from app.core.dependencies import (
    building_indexes,
    tokenizer,
    reciprocal_rank_fusion,
)
from app.core.constants import VECTOR_TOP_K, BM25_TOP_K


logger = logging.getLogger(__name__)


def hybrid_search(query: str):
    if not query or not query.strip():
        raise ValueError("Query cannot be empty.")

    vector_store, bm25, chunks = building_indexes()

    # Semantic search
    vector_results = vector_store.similarity_search(
        query,
        k=VECTOR_TOP_K,
    )

    # Keyword search (BM25)
    scores = bm25.get_scores(
        tokenizer(query)
    )

    top_indices = sorted(
        range(len(scores)),
        key=lambda i: scores[i],
        reverse=True,
    )[:BM25_TOP_K]

    keyword_results = [
        chunks[i]
        for i in top_indices
    ]

    logger.info(
        "Hybrid search completed. Vector results=%d Keyword results=%d",
        len(vector_results),
        len(keyword_results),
    )

    # Merge semantic + keyword results
    return reciprocal_rank_fusion(
        [
            vector_results,
            keyword_results,
        ]
    )