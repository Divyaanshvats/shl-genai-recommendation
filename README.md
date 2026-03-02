# SHL Assessment Recommender

This repository contains an intelligent recommendation system for SHL assessments, built as part of the SHL AI Intern Generative AI assignment.

## Features
- **Scraper:** Robust Selenium-based crawler that extracts 518+ individual SHL assessment listing and detail pages.
- **Retrieval:** Fast vector search using FAISS and `sentence-transformers`.
- **Reranking:** Precision ranking using Google Gemini 1.5 Flash.
- **Balancing:** Logic to ensure a balanced mix of Skill (K) and Personality (P) tests.
- **API:** FastAPI backend with strict schema compliance.
- **UI:** Streamlit frontend for assessment discovery.

## Project Structure
- `app/`: FastAPI application code.
- `data/`: Raw scraped data, embeddings, and FAISS index.
- `scraper/`: Selenium crawler source.
- `recommender/`: Core RAG logic (Retrieval, Reranking, Balancing).
- `evaluation/`: Scripts to calculate Mean Recall@10.
- `frontend/`: Streamlit dashboard.

## Setup & Installation
1. Clone the repository.
2. Install dependencies: `pip install -r requirements.txt`.
3. Set up `.env` with `GEMINI_API_KEY`.
4. Build the index: `python data/build_index.py`.
5. Run the API: `uvicorn app.main:app --reload`.
6. Run the Frontend: `streamlit run frontend/app.py`.

## Evaluation
Run `python evaluation/evaluate.py` to compute Mean Recall@10 on the training dataset.

## Deliverables
- [x] Scraped data (377+ assessments).
- [x] FastAPI Backend with `/recommend` and `/health`.
- [x] Streamlit Frontend.
- [x] `predictions.csv` for the test set.
- [x] 2-page Approach Document.
