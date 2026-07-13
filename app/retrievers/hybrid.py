
from app.core.dependencies import building_indexes , tokenizer , reciprocal_rank_fusion
from app.core.constants import  VECTOR_TOP_K , BM25_TOP_K 

def hybrid_search(query):
    vector_store , bm25, chunks = building_indexes()
    vec = vector_store.similarity_search(query, k=VECTOR_TOP_K)
    print("Collection count:", vector_store._collection.count())

    scores = bm25.get_scores(tokenizer(query))
    idx = sorted(range(len(scores)) , key=lambda i: scores[i], reverse=True)[:BM25_TOP_K]
    kw = [chunks[i] for i in idx]
    return reciprocal_rank_fusion([vec , kw])
