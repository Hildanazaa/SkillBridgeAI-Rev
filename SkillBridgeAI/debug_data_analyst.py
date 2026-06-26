from src.recommender.recommend import recommend_career

# Top 10 dulu biar keliatan posisi Data Analyst
result = recommend_career(
    "python, sql, excel, pandas, numpy, data visualization, power bi",
    top_k=10
)

print("=== TOP 10 REKOMENDASI ===")
for i, r in enumerate(result["recommendations"], 1):
    print(f"{i}. {r['career']} | Score: {r['score']:.2f} | {r['suitability']}")

# Cek detail khusus Data Analyst
print("\n=== CEK DETAIL DATA ANALYST ===")
import json
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from src.recommender.recommend import careers, embeddings, career_to_skills, get_model
from src.skill_extraction.skill_gap import normalize_skill_name

user_skill_text = "python, sql, excel, pandas, numpy, data visualization, power bi"
user_skills_list = [s.strip() for s in user_skill_text.split(",")]
normalized_user = {normalize_skill_name(s) for s in user_skills_list}

aligned_query = "The candidate is proficient and has skills in: " + ", ".join(user_skills_list) + "."
user_embedding = get_model().encode([aligned_query])
similarities = cosine_similarity(user_embedding, embeddings)[0]

for idx, row in careers.iterrows():
    if row["career"].lower() == "data analyst":
        c_skills = {normalize_skill_name(s) for s in career_to_skills.get(row["career"], [])}
        matched = normalized_user.intersection(c_skills)
        matched_count = len(matched)
        total = len(c_skills)
        rasio = matched_count / total
        absolute = matched_count / max(len(normalized_user), 1)
        raw_sim = float(similarities[idx])
        score = (rasio * 40) + (absolute * 30) + (max(0.0, raw_sim) * 30)

        print(f"Career         : {row['career']}")
        print(f"Career Skills  : {sorted(c_skills)}")
        print(f"Matched Skills : {sorted(matched)}")
        print(f"matched_count  : {matched_count}")
        print(f"total_career   : {total}")
        print(f"rasio_match    : {rasio:.4f} ({rasio*40:.2f} poin)")
        print(f"absolute_match : {absolute:.4f} ({absolute*30:.2f} poin)")
        print(f"raw_sim        : {raw_sim:.4f} ({max(0.0,raw_sim)*30:.2f} poin)")
        print(f"FINAL SCORE    : {score:.2f}")
