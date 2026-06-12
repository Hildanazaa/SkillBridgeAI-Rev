import pandas as pd

def normalize_job_title(title: str) -> str:
    t = str(title).strip().lower()
    
    # Standardize spaces and symbols
    t = t.replace("-", " ").replace("/", " ")
    
    # Standardize Frontend
    if "front end" in t or "frontend" in t:
        if "engineer" in t or "developer" in t or "programmer" in t:
            return "Frontend Developer"
            
    # Standardize Backend
    if "back end" in t or "backend" in t:
        if "engineer" in t or "developer" in t or "programmer" in t:
            return "Backend Developer"
            
    # Standardize Fullstack
    if "full stack" in t or "fullstack" in t:
        if "engineer" in t or "developer" in t or "programmer" in t:
            return "Fullstack Developer"
            
    # Standardize UI/UX
    if "ui ux" in t or "uiux" in t or ("user interface" in t and "user experience" in t):
        if "designer" in t or "engineer" in t or "developer" in t:
            return "UI/UX Designer"
            
    # Standardize Mobile Developers
    if "android" in t and ("developer" in t or "engineer" in t):
        return "Android Developer"
    if "ios" in t and ("developer" in t or "engineer" in t):
        return "iOS Developer"
        
    # Standardize Data Analyst
    if "data analyst" in t:
        return "Data Analyst"
    if "data engineer" in t:
        return "Data Engineer"
    if "data scientist" in t:
        return "Data Scientist"

    # Default to a capitalized title
    return " ".join([word.capitalize() for word in str(title).split()])

print("Loading dataset...")

df = pd.read_csv(
    "data/raw/mergeFile.csv",
    low_memory=False
)

print("Normalizing job titles...")
df["jobTitle"] = df["jobTitle"].apply(normalize_job_title)

print("Filtering job titles...")

job_counts = df["jobTitle"].value_counts()

valid_titles = job_counts[
    job_counts > 100
].index

df = df[
    df["jobTitle"].isin(valid_titles)
]

print("Building profiles...")

profiles = []

for title in valid_titles:

    jobs = df[
        df["jobTitle"] == title
    ].head(20)

    for _, job in jobs.iterrows():
        desc = str(job.get("description", "")).strip()
        sp = str(job.get("sellingPoints", "")).strip()

        # Combine title, description, and selling points
        profile_text = f"{title}\n{desc}\n{sp}"

        profiles.append({
            "career": title,
            "profile": profile_text
        })

career_df = pd.DataFrame(
    profiles
)

career_df.to_csv(
    "data/processed/career_profiles_raw.csv",
    index=False
)

print(
    f"Career Profiles Created: {len(career_df)} rows for {len(valid_titles)} unique careers"
)