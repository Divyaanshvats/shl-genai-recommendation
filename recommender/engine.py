"""
Main Recommendation Engine
Orchestrates: Retrieve -> Rerank -> Balance
"""

from recommender.retriever import Retriever
from recommender.reranker import Reranker
from recommender.balancer import Balancer

class RecommendationEngine:
    def __init__(self):
        self.retriever = Retriever()
        self.reranker = Reranker()
        self.balancer = Balancer()

    def get_recommendations(self, query: str, limit: int = 10):
        # 1. Retrieval (FAISS - fast)
        # Get 30 candidates for better reranking pool
        candidates = self.retriever.retrieve(query, top_k=30)
        
        if not candidates:
            return []

        # 2. Reranking (LLM - precise)
        # Get top 20 reranked
        # (The reranker internal logic handles sub-sampling)
        reranked = self.reranker.rerank(query, candidates, top_k=20)

        # 3. Balancing (Mix types)
        final_balanced = self.balancer.balance(reranked, query, limit=limit)

        return final_balanced
