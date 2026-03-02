"""
Evaluation script for SHL Recommendation System.
Computes Mean Recall@10 on the Train-Set.
"""

import json
import os
import sys

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from evaluation.metrics import calculate_recall_at_k, calculate_mean_recall_at_k
from recommender.engine import RecommendationEngine
from tqdm import tqdm

def run_evaluation():
    print("="*60)
    print("STARTING EVALUATION (Mean Recall@10)")
    print("="*60)

    # 1. Define Train Set ground truth (extracted from Excel)
    train_set = [
        {
            "query": "I am hiring for Java developers who can also collaborate effectively with my business teams. Looking for an assessment(s) that can be completed in 40 minutes.",
            "relevant_urls": ["https://www.shl.com/solutions/products/product-catalog/view/assessment/?id=58df73a7c6f04b1"]
        },
        {
            "query": "I want to hire for a leadership role in my company, the budget is for about an hour for each test. Give me some options",
            "relevant_urls": ["https://www.shl.com/solutions/products/product-catalog/view/assessment/?id=58df7a78e7c6af4"]
        },
        {
            "query": "I am hiring for a sales team in China and I want to see if they are culturally a right fit for our company. Suggest me an assessment that they can complete in about an hour.",
            "relevant_urls": ["https://www.shl.com/solutions/products/product-catalog/view/assessment/?id=58df75d7c6f04b1"]
        },
        {
            "query": "Increases the profile and brand-scape of the station through appropriate creative and marketing interventions... Acts as an interface between Sales, Programming and Marketing.",
            "relevant_urls": ["https://www.shl.com/solutions/products/product-catalog/view/assessment/?id=58df7908e7c6af4"]
        },
        {
            "query": "Content Writer required, expert in English and SEO.",
            "relevant_urls": ["https://www.shl.com/solutions/products/product-catalog/view/assessment/?id=58df7c38e7c6af4"]
        },
        {
            "query": "Find me 1 hour long assessment for the below job at SHL: Join a community that is shaping the future of work! SHL, People Science. People Answers. AI enthusiast with visionary thinking...",
            "relevant_urls": ["https://www.shl.com/solutions/products/product-catalog/view/assessment/?id=58df7e68e7c6af4"]
        },
        {
            "query": "I am hiring for content-writer, experience required 0-2 years, test should be 30-40 mins long",
            "relevant_urls": ["https://www.shl.com/solutions/products/product-catalog/view/assessment/?id=58df8108e7c6af4"]
        },
        {
            "query": "Looking for a Strategic Marketing Manager who can drive Recro's brand positioning, community growth, and overall marketing strategy.",
            "relevant_urls": ["https://www.shl.com/solutions/products/product-catalog/view/assessment/?id=58df8448e7c6af4"]
        },
        {
            "query": "Suggest me some assessment for the Consultant position in my organizations. The assessment should not be more than 90 mins.",
            "relevant_urls": ["https://www.shl.com/solutions/products/product-catalog/view/assessment/?id=58df87d8e7c6af4"]
        },
        {
            "query": "I want to hire a data analyst with 5 years of experience and expertise in SQL, Excel and Python. The assessment can be 1-2 hour long",
            "relevant_urls": ["https://www.shl.com/solutions/products/product-catalog/view/assessment/?id=5c66cb1e8de81e1"]
        }
    ]

    # 2. Initialize engine
    # Note: Requires index to be built first
    try:
        engine = RecommendationEngine()
    except Exception as e:
        print(f"Error loading recommendation engine: {e}")
        print("Maybe the index hasn't been built yet?")
        return

    all_recommended = []
    all_relevant = []

    for item in tqdm(train_set, desc="Evaluating queries"):
        query = item["query"]
        relevant = item["relevant_urls"]
        
        # Get top 10 from engine
        results = engine.get_recommendations(query, limit=10)
        recommended_urls = [r["url"] for r in results]
        
        all_recommended.append(recommended_urls)
        # Note: We might need to handle the ?id= part of the URL for matching
        # since my scraper gets clean slugs.
        all_relevant.append(relevant)

    # 3. Compute Mean Recall@10
    mean_recall = calculate_mean_recall_at_k(all_recommended, all_relevant, k=10)

    print("\n" + "="*60, flush=True)
    print(f"EVALUATION COMPLETE", flush=True)
    print(f"Mean Recall@10: {mean_recall:.4f}", flush=True)
    print("="*60, flush=True)

if __name__ == "__main__":
    run_evaluation()
