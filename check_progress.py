import json
import os

def check_status():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    files = ["data/raw/assessments.json", "data/raw/assessments_raw.json", "scraper_log.txt"]
    for f in files:
        full_path = os.path.join(base_dir, f)
        if os.path.exists(full_path):
            size = os.path.getsize(full_path)
            print(f"File: {f}, Size: {size} bytes")
            if f.endswith(".json"):
                try:
                    with open(full_path, "r", encoding="utf-8") as jf:
                        data = json.load(jf)
                        print(f"  Items: {len(data)}")
                except Exception as e:
                    print(f"  Error reading JSON: {e}")
        else:
            print(f"File: {f} does not exist")

if __name__ == "__main__":
    check_status()
