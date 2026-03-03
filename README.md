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

A FEW TESTED RESULTS ARE AS FOLLOWS:
<img width="1887" height="998" alt="image" src="https://github.com/user-attachments/assets/6b068330-963b-4727-b8a5-2c9bb78cd180" />
<img width="1872" height="1001" alt="image" src="https://github.com/user-attachments/assets/d915a4f5-12a4-43d9-97ab-0f8bfc219caa" />
<img width="1887" height="1002" alt="image" src="https://github.com/user-attachments/assets/906b7c7c-8575-476e-9b9d-5d5c9d3ee201" />
<img width="1886" height="1011" alt="image" src="https://github.com/user-attachments/assets/6ae31719-fba4-4330-b651-8e05c4feb903" />
<img width="1890" height="992" alt="image" src="https://github.com/user-attachments/assets/f19597af-14e5-4067-92a9-e5d9821b8e95" />
<img width="1892" height="990" alt="image" src="https://github.com/user-attachments/assets/6e91183f-26f1-44f0-9797-c86434d64b94" />
<img width="1882" height="1006" alt="image" src="https://github.com/user-attachments/assets/b970dbdb-9d1c-4d3e-b7d0-1ff976e4e3bb" />





