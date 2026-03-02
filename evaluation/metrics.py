"""
Evaluation Metrics for SHL Recommendation System
"""

import numpy as np

def calculate_recall_at_k(recommended_urls, relevant_urls, k=10):
    """
    Calculate Recall@K for a single query.
    """
    if not relevant_urls:
        return 0.0
    
    # Take top K recommendations
    recommended_k = recommended_urls[:k]
    
    # Intersection of recommended and relevant
    hits = len(set(recommended_k) & set(relevant_urls))
    
    return hits / len(relevant_urls)

def calculate_mean_recall_at_k(all_recommendations, all_relevance_labels, k=10):
    """
    Calculate Mean Recall@K across all queries.
    all_recommendations: list of lists of recommended URLs
    all_relevance_labels: list of lists of relevant URLs
    """
    recalls = []
    for recommended, relevant in zip(all_recommendations, all_relevance_labels):
        recalls.append(calculate_recall_at_k(recommended, relevant, k))
    
    return np.mean(recalls) if recalls else 0.0
