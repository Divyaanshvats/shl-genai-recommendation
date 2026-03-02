"""
Retrieves top candidates from the FAISS index.
"""

import faiss
import pickle
import numpy as np
import os
import gc
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
            print(f"Loading FAISS index from {INDEX_PATH}...")
            # Use mmap to load index from disk without consuming RAM
            self.index = faiss.read_index(INDEX_PATH, faiss.IO_FLAG_MMAP)
            
            print(f"Loading metadata from {METADATA_PATH}...")
            with open(METADATA_PATH, "rb") as f:
                self.metadata = pickle.load(f)
            
            print(f"Loading SentenceTransformer model ({MODEL_NAME})...")
            # Note: This might take time on first run as it downloads weights
            self.model = SentenceTransformer(MODEL_NAME)
            
            # Force garbage collection to free up any temporary boot memory
            gc.collect()
            print("Resources loaded successfully.")
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
