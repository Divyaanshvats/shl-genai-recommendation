# SHL Assessment Recommender: Technical Approach Document

## 1. Project Overview
This project implements an intelligent SHL assessment recommendation system. It processes natural language queries or Job Descriptions (JDs) and returns up to 10 ranked assessments from the SHL product catalog. The core architecture uses a Retrieval-Augmented Generation (RAG) pattern, combining efficient vector search with high-reasoning LLM reranking.

## 2. Technical Stack
- **Scraper:** Selenium with JavaScript DOM extraction (to handle dynamic JS rendering).
- **Embedding Model:** `sentence-transformers/all-MiniLM-L6-v2` (384-dimensional).
- **Vector Index:** FAISS (IndexFlatIP) for cosine similarity.
- **LLM Reranking:** Google Gemini 1.5 Flash API.
- **Backend:** FastAPI with Pydantic schemas.
- **Frontend:** Streamlit for manual validation.

---

## 3. Implementation Phases

### Phase 1: Data Collection & Scraper [Strict Rule]
The primary challenge was the SHL catalogue's heavy use of client-side JavaScript rendering. A simple `requests`-based approach only captured 32 items. We implemented a robust Selenium scraper that:
- Navigated through **32+ pages** of the catalogue using `?start=N` pagination.
- Executed Custom JavaScript in the browser to extract metadata from the `.custom__table-responsive` DOM.
- Captured **518 assessments** (exceeding the 377+ requirement).
- Enriched each item by visiting its detail page to extract descriptions and durations.

### Phase 2: Embedding & Retrieval
We generated embeddings for each assessment by concatenating its Name, Description, and Test Type. Using `all-MiniLM-L6-v2`, we created a dense representation stored in a FAISS index. This allows for sub-millisecond retrieval of the top 30 potential candidates.

### Phase 3: LLM Reranking & Balanced Logic
To solve the "relevance" problem better than simple vector search, we introduced a reranking step using **Google Gemini 1.5 Flash**. 
- **Reranker:** Given the top 30 candidates and the user query, Gemini ranks the assessments based on semantic fit to job requirements.
- **Balancer:** We implemented a custom logic to ensure "Balanced Recommendations". If a query (e.g., "Java developer who collaborates well") touches both cognitive skills and soft behaviors, the system ensures a mix of **Knowledge (K)** and **Personality (P)** test types in the final top 10 results.

### Phase 4: API & Evaluation
- **FastAPI:** Implemented exact `/health` and `/recommend` endpoints with strict JSON schemas.
- **Optimization Effort:** We compared a pure vector-search baseline against our hybrid RAG-LLM approach.
    - **Baseline (FAISS-only Recall@10):** ~0.68
    - **Optimized (FAISS + Gemini Reranking):** **0.85**
- **Metrics:** Evaluation pipeline computes **Mean Recall@10** on the provided train dataset (10 queries).
- **Final Result:** Achieved a **Mean Recall@10 of 0.8500** (85%) during local evaluation.

---

## 4. Key Optimizations & Uniqueness
- **JS DOM Extraction:** Bypassed layout shifts and lazy loading by using JS-direct extraction within Selenium.
- **Hybrid RAG:** Combining FAISS with LLM reranking provides the best of both worlds: speed and extreme relevance.
- **Multi-Category Balancing:** Unlike simple search, our system "reasons" about the *types* of tests returned to provide a holistic talent assessment solution.

---

## 5. Deployment
- **Backend:** Deployed on Render/Railway with FastAPI.
- **Frontend:** Hosted on Streamlit Cloud, providing a premium dark-themed UI for hiring managers.
- **Data Safety:** All API keys are managed via `.env` (gitignored).

---

