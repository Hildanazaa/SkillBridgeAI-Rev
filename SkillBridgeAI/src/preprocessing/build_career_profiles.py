import pandas as pd
import re

def clean_title(title):
    title = str(title).split("-")[0]
    title = re.sub(
        r"\b(entry level|entry-level|junior|senior|intern|trainee|fresher|experienced)\b",
        "",
        title,
        flags=re.IGNORECASE
    )
    title = re.sub(r"\s+", " ", title).strip()
    # Ensure Title Case capitalization
    title = " ".join([word.capitalize() for word in title.split()])
    return title

print("Loading dataset...")
df = pd.read_csv(
    "data/raw/job_dataset.csv",
    low_memory=False
)

# Drop rows with null Titles
df = df.dropna(subset=["Title"])

print("Normalizing job titles...")
df["career"] = df["Title"].apply(clean_title)

print("Building profiles...")
profiles = []

for idx, job in df.iterrows():
    title = job["Title"]
    career = job["career"]
    skills = str(job.get("Skills", "")).strip()
    resp = str(job.get("Responsibilities", "")).strip()
    kw = str(job.get("Keywords", "")).strip()
    exp_level = str(job.get("ExperienceLevel", "")).strip()
    y_exp = str(job.get("YearsOfExperience", "")).strip()

    # Combine details for embedding text profile
    profile_text = f"{title}\nSkills: {skills}\nResponsibilities: {resp}\nKeywords: {kw}"

    profiles.append({
        "career": career,
        "Title": title,
        "ExperienceLevel": exp_level,
        "YearsOfExperience": y_exp,
        "Skills": skills,
        "Responsibilities": resp,
        "Keywords": kw,
        "profile": profile_text
    })

career_df = pd.DataFrame(profiles)
career_df.to_csv(
    "data/processed/career_profiles_raw.csv",
    index=False
)

print(
    f"Career Profiles Created: {len(career_df)} rows for {career_df['career'].nunique()} unique careers"
)