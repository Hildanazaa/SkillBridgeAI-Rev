import json

with open(
    "data/processed/career_skills.json",
    "r",
    encoding="utf-8"
) as f:
    data = json.load(f)

targets = [
    "Frontend Developer",
    "Front End Developer",
    "Backend Developer",
    "Software Engineer",
    "Data Analyst",
    "UI/UX Designer",
    "Fullstack Engineer"
]

for item in data:

    if item["career"] in targets:

        print("\n" + "=" * 50)
        print("Career :", item["career"])
        print("Skills :", item["skills"])