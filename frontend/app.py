"""
Streamlit Frontend for SHL Recommendation System
"""

import streamlit as st
import requests
import pandas as pd
import os

API_URL = os.getenv("API_URL", "http://127.0.0.1:8000")

st.set_page_config(
    page_title="SHL Assessment Recommender",
    page_icon="🔍",
    layout="wide"
)

st.title("🔍 SHL Assessment Recommender")
st.markdown("""
Welcome to the **SHL Assessment Recommendation System**. 
Enter a Job Description (JD) or a natural language query below to find the most relevant SHL assessments.
""")

query = st.text_area("Enter your query or Job Description:", height=150, placeholder="e.g., Hiring for a Java developer with strong communication skills...")

if st.button("Get Recommendations"):
    if query:
        with st.spinner("Analyzing and retrieving the best assessments..."):
            try:
                response = requests.post(f"{API_URL}/recommend", json={"query": query})
                if response.status_code == 200:
                    data = response.json()
                    recommendations = data.get("recommended_assessments", [])
                    
                    if recommendations:
                        st.success(f"Found {len(recommendations)} relevant assessments!")
                        
                        # Display results in a table-like format
                        for i, item in enumerate(recommendations):
                            with st.container():
                                col1, col2 = st.columns([1, 4])
                                with col1:
                                    st.write(f"### {i+1}")
                                with col2:
                                    st.markdown(f"### [{item['name']}]({item['url']})")
                                    st.write(f"**Type:** {', '.join(item['test_type'])}")
                                    st.write(f"**Description:** {item['description']}")
                                    
                                    # Extra details
                                    inner_col1, inner_col2, inner_col3 = st.columns(3)
                                    inner_col1.metric("Duration", f"{item['duration']} mins")
                                    inner_col2.metric("Adaptive", item['adaptive_support'])
                                    inner_col3.metric("Remote", item['remote_support'])
                                    
                                st.divider()
                    else:
                        st.warning("No relevant assessments found. Try refining your query.")
                else:
                    st.error(f"API Error ({response.status_code}): {response.text}")
                    st.info(f"Requested URL: {API_URL}/recommend")
            except Exception as e:
                st.error(f"Connection Failed: {e}")
                st.info(f"Is the backend running at {API_URL}?")
    else:
        st.warning("Please enter a query first.")

# Footer
st.sidebar.title("About")
st.sidebar.info("""
This system uses:
- **FAISS** for fast vector search
- **Sentence-Transformers** for embeddings
- **Google Gemini 1.5** for LLM reranking
- **FastAPI** backend
- **Streamlit** frontend
""")
