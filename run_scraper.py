"""
Full SHL scraper pipeline using Selenium.
"""

import json
import os
import sys

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from scraper.selenium_crawler import run_selenium_scraper

FINAL_PATH = "data/raw/assessments.json"

def run_full_pipeline():
    print("\n" + "="*60)
    print("RUNNING FULL SHL SCRAPER PIPELINE (SELENIUM)")
    print("="*60)
    
    enriched = run_selenium_scraper()

    if not enriched:
        print("ERROR: No assessments scraped!")
        sys.exit(1)

    # Step 3: Save final output
    print("\n" + "="*60)
    print("SAVING FINAL ASSESSMENTS")
    print("="*60)
    os.makedirs(os.path.dirname(FINAL_PATH), exist_ok=True)
    with open(FINAL_PATH, "w", encoding="utf-8") as f:
        json.dump(enriched, f, indent=2, ensure_ascii=False)

    print(f"\nFINAL RESULT:")
    print(f"  Total assessments: {len(enriched)}")
    print(f"  Target (377+): {'MET ✓' if len(enriched) >= 377 else 'NOT MET ✗'}")
    print(f"  Saved to: {FINAL_PATH}")

    # Print sample
    if enriched:
        print(f"\nSample assessment:")
        sample = enriched[0]
        for k, v in sample.items():
            print(f"  {k}: {v!r}")

    return enriched

if __name__ == "__main__":
    run_full_pipeline()
