import pandas as pd
import json
import re
from src.skill_extraction.skills import SKILLS

df = pd.read_csv(
    "data/processed/career_profiles_raw.csv"
)

grouped_df = df.groupby("career")["profile"].apply(lambda x: " ".join(x.astype(str))).reset_index()

career_skills = []

for _, row in grouped_df.iterrows():

    career = row["career"]

    profile = str(
        row["profile"]
    ).lower()

    profile = profile.replace("reactjs", "react").replace("react.js", "react").replace("react js", "react")
    profile = profile.replace("nextjs", "next.js").replace("next js", "next.js")
    profile = profile.replace("nodejs", "node.js").replace("node js", "node.js")
    profile = profile.replace("nestjs", "nestjs").replace("nest.js", "nestjs").replace("nest js", "nestjs")
    profile = profile.replace("expressjs", "express").replace("express js", "express")
    profile = profile.replace("restapi", "rest api").replace("rest api", "rest api")
    profile = profile.replace("powerbi", "power bi").replace("power bi", "power bi")
    profile = profile.replace("googleads", "google ads").replace("google ads", "google ads")
    profile = profile.replace("metaads", "meta ads").replace("meta ads", "meta ads")
    
    profile = profile.replace("go lang", "golang")
    profile = profile.replace("tailwindcss", "tailwind")
    profile = profile.replace("komunikasi", "communication")
    profile = profile.replace("kerja sama", "teamwork").replace("kerjasama", "teamwork")
    profile = profile.replace("kepemimpinan", "leadership")
    profile = profile.replace("pemecahan masalah", "problem solving")
    profile = profile.replace("kemampuan analitis", "analytical skills").replace("berpikir analitis", "analytical skills").replace("analisis", "analytical skills")
    profile = profile.replace("kolaborasi", "collaboration")
    profile = profile.replace("negosiasi", "negotiation")

    found_skills = []

    for skill in SKILLS:
        start_boundary = r'\b' if (skill[0].isalnum() or skill[0] == '_') else ''
        end_boundary = r'\b' if (skill[-1].isalnum() or skill[-1] == '_') else ''
        pattern = start_boundary + re.escape(skill) + end_boundary

        if re.search(pattern, profile):
            found_skills.append(skill)

    career_skills.append({
        "career": career,
        "skills": sorted(
            list(set(found_skills))
        )
    })

with open(
    "data/processed/career_skills.json",
    "w",
    encoding="utf-8"
) as f:

    json.dump(
        career_skills,
        f,
        ensure_ascii=False,
        indent=4
    )

print(
    f"Career Skills Created: {len(career_skills)}"
)

for item in career_skills[:5]:

    print("\nCareer:", item["career"])
    print("Skills:", item["skills"])