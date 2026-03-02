"""
Builds an embedding index for the scraped assessments using sentence-transformers and FAISS.
"""

import json
import os
import faiss
import numpy as np
import pickle
from sentence_transformers import SentenceTransformer
from tqdm import tqdm

DATA_PATH = "data/raw/assessments.json"
INDEX_PATH = "data/embeddings/faiss.index"
METADATA_PATH = "data/embeddings/metadata.pkl"
MODEL_NAME = "all-MiniLM-L6-v2"

def build_index():
    print("="*60)
    print("Building Embedding Index")
    print("="*60)

    if not os.path.exists(DATA_PATH):
        print(f"ERROR: {DATA_PATH} not found. Run scraper first.")
        return

    with open(DATA_PATH, "r", encoding="utf-8") as f:
        assessments = json.load(f)

    if not assessments:
        print("ERROR: No assessments found in JSON.")
        return

    print(f"Loaded {len(assessments)} assessments.")

    # Prepare text for embedding
    # Combine name, description and test types for a rich text representation
    texts = []
    for a in assessments:
        name = a.get("name", "")
        desc = a.get("description", "")
        types = ", ".join(a.get("test_type", []))
        # Format: "Name: ... Description: ... Types: ..."
        text = f"Assessment: {name}. Description: {desc}. Types: {types}."
        texts.append(text)

    print(f"Loading model: {MODEL_NAME}...")
    model = SentenceTransformer(MODEL_NAME)

    print("Generating embeddings...")
    embeddings = model.encode(texts, show_progress_bar=True, convert_to_numpy=True)

    # Normalize embeddings for cosine similarity
    faiss.normalize_L2(embeddings)

    # Build FAISS index
    dimension = embeddings.shape[1]
    # Using IndexFlatIP for Inner Product (Cosine similarity since we normalized)
    index = faiss.IndexFlatIP(dimension)
    index.add(embeddings)

    # Save index and metadata
    os.makedirs(os.path.dirname(INDEX_PATH), exist_ok=True)
    faiss.write_index(index, INDEX_PATH)
    
    with open(METADATA_PATH, "wb") as f:
        pickle.dump(assessments, f)

    print(f"\nSUCCESS:")
    print(f"  Index saved to: {INDEX_PATH}")
    print(f"  Metadata saved to: {METADATA_PATH}")
    print(f"  Dimension: {dimension}")
    print(f"  Total items: {index.ntotal}")
    print("="*60)

if __name__ == "__main__":
    build_index()
