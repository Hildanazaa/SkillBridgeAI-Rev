import pandas as pd
import numpy as np
import json
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from src.skill_extraction.skill_gap import normalize_skill_name


# load sekali saja (biar cepat)
careers = pd.read_csv("data/processed/career_profiles.csv")
embeddings = np.load("data/embeddings/career_embeddings.npy")

# Filter out careers that have 0 required skills in the skill database
with open("data/processed/career_skills.json", "r", encoding="utf-8") as f:
    career_skills_data = json.load(f)

career_skills_dict = {item["career"]: item["skills"] for item in career_skills_data}
valid_careers = {item["career"] for item in career_skills_data if len(item["skills"]) > 0}

mask = careers["career"].isin(valid_careers)
careers = careers[mask].reset_index(drop=True)
embeddings = embeddings[mask]

model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")


def recommend_career(user_skill_text: str, top_k: int = 5):
    # Normalize user skills
    user_skills_list = [s.strip() for s in user_skill_text.split(",") if s.strip()]
    normalized_user_skills = {normalize_skill_name(s) for s in user_skills_list}

    user_embedding = model.encode([user_skill_text])

    similarities = cosine_similarity(
        user_embedding,
        embeddings
    )[0]

    hybrid_recommendations = []

    for idx, row in careers.iterrows():
        career_name = row["career"]
        semantic_score = float(similarities[idx] * 100)

        # Get career skills
        career_skills = career_skills_dict.get(career_name, [])
        normalized_career_skills = {normalize_skill_name(s) for s in career_skills}

        # Calculate overlap
        overlap_count = len(normalized_user_skills.intersection(normalized_career_skills))

        # Boost score by 15 points per matching skill
        boosted_score = semantic_score + (overlap_count * 15.0)

        hybrid_recommendations.append({
            "career": career_name,
            "score": boosted_score,
            "semantic_score": semantic_score,
            "overlap_count": overlap_count
        })

    # Sort by hybrid score descending
    hybrid_recommendations = sorted(hybrid_recommendations, key=lambda x: x["score"], reverse=True)

    # Take top k
    recommendations = []
    for item in hybrid_recommendations[:top_k]:
        recommendations.append({
            "career": item["career"],
            "score": float(item["score"])
        })

    return {
        "success": True,
        "recommendations": recommendations
    }