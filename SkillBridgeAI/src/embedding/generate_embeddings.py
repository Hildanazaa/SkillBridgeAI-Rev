import os
import warnings
import logging

warnings.filterwarnings("ignore")
os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"
os.environ["HF_HUB_DISABLE_IMPLICIT_TOKEN_WARNING"] = "1"
# os.environ["HF_HUB_OFFLINE"] = "1"
# os.environ["TRANSFORMERS_OFFLINE"] = "1"
try:
    from huggingface_hub.utils import disable_progress_bars
    disable_progress_bars()
except ImportError:
    pass

logging.getLogger("sentence_transformers").setLevel(logging.WARNING)
logging.getLogger("transformers").setLevel(logging.ERROR)

import pandas as pd
import numpy as np
from sentence_transformers import SentenceTransformer

print("Loading career profiles raw...")
df = pd.read_csv(
    "data/processed/career_profiles_raw.csv"
)

print("Loading model all-MiniLM-L6-v2...")
model = SentenceTransformer(
    "all-MiniLM-L6-v2"
)

print("Generating embeddings with averaging...")
unique_careers = df["career"].unique()
unique_embeddings = []

for i, career in enumerate(unique_careers):
    profiles = df[df["career"] == career]["profile"].tolist()
    
    emb = model.encode(
        profiles,
        show_progress_bar=False,
        convert_to_numpy=True
    )
    
    avg_emb = np.mean(emb, axis=0)
    unique_embeddings.append(avg_emb)
    
    if (i + 1) % 50 == 0 or (i + 1) == len(unique_careers):
        print(f"Processed {i + 1}/{len(unique_careers)} careers")

embeddings_array = np.array(unique_embeddings)

np.savetxt(
    "data/embeddings/career_embeddings.csv",
    embeddings_array,
    delimiter=","
)

# Group by career and aggregate columns to preserve them in career_profiles.csv
# This is required because scoring.py loads career_profiles.csv directly and expects Title, Skills, Keywords, Responsibilities
def combine_unique_skills(series):
    skills = set()
    for row in series.dropna():
        for skill in str(row).replace(";", ",").split(","):
            skill = skill.strip()
            if skill:
                skills.add(skill)
    return "; ".join(sorted(skills))

def combine_unique_keywords(series):
    keywords = set()
    for row in series.dropna():
        for kw in str(row).replace(";", ",").split(","):
            kw = kw.strip()
            if kw:
                keywords.add(kw)
    return " ".join(sorted(keywords))

unique_careers_df = df.groupby("career", as_index=False).agg({
    "Skills": combine_unique_skills,
    "Keywords": combine_unique_keywords,
    "Responsibilities": lambda x: " ".join(x.dropna().astype(str))
})
unique_careers_df["Title"] = unique_careers_df["career"]
unique_careers_df = unique_careers_df[["career", "Title", "Skills", "Keywords", "Responsibilities"]]

unique_careers_df.to_csv(
    "data/processed/career_profiles.csv",
    index=False
)

print("Saved embeddings and unique careers list with all scoring columns.")
print("Shape:", embeddings_array.shape)