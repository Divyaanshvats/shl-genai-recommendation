import json
import os

path = r"data/raw/assessments.json"
if os.path.exists(path):
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
        print(f"Total Assessments in JSON: {len(data)}")
        enriched = [x for x in data if x.get("description") and len(x["description"]) > 50]
        print(f"Enriched Assessments: {len(enriched)}")
else:
    print("File not found.")
