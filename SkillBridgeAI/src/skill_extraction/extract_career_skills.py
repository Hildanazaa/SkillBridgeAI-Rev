import pandas as pd
import json
import re
from src.skill_extraction.skills import SKILLS

# Load career profiles
df = pd.read_csv(
    "data/processed/career_profiles_raw.csv"
)

# Group profiles by career title to aggregate descriptions for extraction
grouped_df = df.groupby("career")["profile"].apply(lambda x: " ".join(x.astype(str))).reset_index()

career_skills = []

for _, row in grouped_df.iterrows():

    career = row["career"]

    profile = str(
        row["profile"]
    ).lower()

    # Normalize spelling variations in the job posting text before word boundary matching
    profile = profile.replace("reactjs", "react").replace("react.js", "react").replace("react js", "react")
    profile = profile.replace("nextjs", "next.js").replace("next js", "next.js")
    profile = profile.replace("nodejs", "node.js").replace("node js", "node.js")
    profile = profile.replace("nestjs", "nestjs").replace("nest.js", "nestjs").replace("nest js", "nestjs")
    profile = profile.replace("expressjs", "express").replace("express js", "express")
    profile = profile.replace("restapi", "rest api").replace("rest api", "rest api")
    profile = profile.replace("powerbi", "power bi").replace("power bi", "power bi")
    profile = profile.replace("googleads", "google ads").replace("google ads", "google ads")
    profile = profile.replace("metaads", "meta ads").replace("meta ads", "meta ads")

    found_skills = []

    for skill in SKILLS:
        # Check matching with word boundaries
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

# Save JSON
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

# Preview
for item in career_skills[:5]:

    print("\nCareer:", item["career"])
    print("Skills:", item["skills"])