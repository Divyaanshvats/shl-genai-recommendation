"""
Retrieves top candidates from the FAISS index.
"""

import faiss
import pickle
import numpy as np
import os
from sentence_transformers import SentenceTransformer

INDEX_PATH = "data/embeddings/faiss.index"
METADATA_PATH = "data/embeddings/metadata.pkl"
MODEL_NAME = "all-MiniLM-L6-v2"

class Retriever:
    def __init__(self):
        self.model = None
        self.index = None
        self.metadata = None
        self.load_resources()

    def load_resources(self):
        if os.path.exists(INDEX_PATH) and os.path.exists(METADATA_PATH):
            print(f"Loading retriever resources from {os.path.dirname(INDEX_PATH)}...")
            self.index = faiss.read_index(INDEX_PATH)
            with open(METADATA_PATH, "rb") as f:
                self.metadata = pickle.load(f)
            self.model = SentenceTransformer(MODEL_NAME)
        else:
            print("WARNING: Retriever resources not found. Build the index first.")

    def retrieve(self, query: str, top_k: int = 20):
        if self.index is None or self.model is None:
            return []

        # Encode query
        query_vector = self.model.encode([query], convert_to_numpy=True)
        faiss.normalize_L2(query_vector)

        # Search
        scores, indices = self.index.search(query_vector, top_k)
        
        results = []
        for score, idx in zip(scores[0], indices[0]):
            if idx < len(self.metadata):
                item = self.metadata[idx].copy()
                item["score"] = float(score)
                results.append(item)
        
        return results
