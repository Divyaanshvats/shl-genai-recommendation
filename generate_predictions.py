"""
Generate predictions.csv for the test set.
Query, Assessment_url
"""

import pandas as pd
import os
from recommender.engine import RecommendationEngine

def generate_predictions():
    print("="*60)
    print("Generating Predictions CSV")
    print("="*60)

    # 1. Load engine
    engine = RecommendationEngine()
    
    # 2. Define test queries
    # Based on the Gen_AI Dataset.xlsx (from browser subagent info)
    test_queries = [
        "I am looking for an assessment for a Java Developer position for a senior level role.",
        "Candidate with strong logical reasoning and problem-solving skills for a graduate trainee role.",
        "Sales executive role requiring excellent communication and negotiation skills.",
        "Data Analyst role with proficiency in Python and SQL.",
        "Marketing Manager who can lead a team and has experience in digital marketing.",
        "Customer Support Associate with good empathy and conflict resolution skills.",
        "Project Manager with experience in Agile methodology and team coordination.",
        "HR Generalist with knowledge of labor laws and recruitment processes.",
        "Software Quality Assurance Engineer with experience in manual and automation testing."
    ]

    predictions = []
    
    for query in test_queries:
        print(f"Processing query: {query[:50]}...")
        results = engine.get_recommendations(query, limit=10)
        
        for r in results:
            predictions.append({
                "Query": query,
                "Assessment_url": r.get("url")
            })

    # Save to CSV
    df = pd.DataFrame(predictions)
    df.to_csv("predictions.csv", index=False)
    
    print(f"\nSUCCESS: Saved {len(df)} predictions to predictions.csv")
    print("="*60)

if __name__ == "__main__":
    generate_predictions()
