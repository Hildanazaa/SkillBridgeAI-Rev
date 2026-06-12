import json

with open(
    "data/processed/career_skills.json",
    "r",
    encoding="utf-8"
) as f:
    data = json.load(f)

for item in data:
    print(item["career"])