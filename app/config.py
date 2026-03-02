"""
FastAPI Configuration
"""

import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    INDEX_PATH = "data/embeddings/faiss.index"
    METADATA_PATH = "data/embeddings/metadata.pkl"
    PORT = 8000
    HOST = "0.0.0.0"

config = Config()
