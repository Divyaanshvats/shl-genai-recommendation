"""
Reranks candidates using Google Gemini LLM for better relevance.
"""

import google.generativeai as genai
import os
import json
from dotenv import load_dotenv

load_dotenv()

class Reranker:
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        if api_key:
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel('gemini-1.5-flash')
        else:
            print("WARNING: GEMINI_API_KEY not found in .env")
            self.model = None

    def rerank(self, query: str, candidates: list[dict], top_k: int = 10):
        if not self.model or not candidates:
            return candidates[:top_k]

        # Prepare context for LLM
        # Only take top 20 candidates for reranking to save tokens and time
        candidates_to_rerank = candidates[:20]
        
        candidates_text = ""
        for i, c in enumerate(candidates_to_rerank):
            candidates_text += f"[{i}] Name: {c.get('name')}\n"
            candidates_text += f"Description: {c.get('description')}\n"
            candidates_text += f"Types: {', '.join(c.get('test_type', []))}\n\n"

        prompt = f"""
You are an expert recruitment consultant specialized in SHL assessments.
The user's query/JD is: "{query}"

Below is a list of candidate SHL assessments retrieved from the catalog. 
Rank them from 1 to {len(candidates_to_rerank)} based on how relevant they are to the user's query.
Higher rank (1) means more relevant.

Return ONLY a JSON array of indices in the order of most relevant to least relevant.
Example format: [5, 2, 0, 8, ...]

Candidates:
{candidates_text}

JSON Array:
"""

        try:
            response = self.model.generate_content(prompt)
            # Find the JSON array in the text
            import re
            match = re.search(r'\[[\d,\s]*\]', response.text)
            if match:
                indices = json.loads(match.group(0))
                
                # Rebuild the list based on LLM ranking
                ranked_results = []
                seen_indices = set()
                for idx in indices:
                    if 0 <= idx < len(candidates_to_rerank) and idx not in seen_indices:
                        ranked_results.append(candidates_to_rerank[idx])
                        seen_indices.add(idx)
                
                # Add remaining if LLM missed any
                for i, c in enumerate(candidates_to_rerank):
                    if i not in seen_indices:
                        ranked_results.append(c)
                
                # Add remaining candidates that weren't sent to LLM
                ranked_results.extend(candidates[20:])
                
                return ranked_results[:top_k]
            else:
                return candidates[:top_k]
        except Exception as e:
            print(f"Error during reranking: {e}")
            return candidates[:top_k]
