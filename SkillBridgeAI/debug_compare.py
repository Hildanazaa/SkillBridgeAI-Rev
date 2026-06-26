from src.recommender.recommend import careers, embeddings, career_to_skills, get_model
from src.skill_extraction.skill_gap import normalize_skill_name
from sklearn.metrics.pairwise import cosine_similarity

user_skill_text = "python, sql, excel, pandas, numpy, data visualization, power bi"
user_skills_list = [s.strip() for s in user_skill_text.split(",")]
normalized_user = {normalize_skill_name(s) for s in user_skills_list}

print(f"User skills (normalized): {sorted(normalized_user)}\n")

aligned_query = "The candidate is proficient and has skills in: " + ", ".join(user_skills_list) + "."
user_embedding = get_model().encode([aligned_query])
similarities = cosine_similarity(user_embedding, embeddings)[0]

targets = ["Data Analyst", "Data Scientist", "Machine Learning Engineer"]

for idx, row in careers.iterrows():
    if row["career"] in targets:
        c_skills = {normalize_skill_name(s) for s in career_to_skills.get(row["career"], [])}
        matched = normalized_user.intersection(c_skills)
        matched_count = len(matched)
        total = len(c_skills)
        rasio = matched_count / total
        absolute = matched_count / max(len(normalized_user), 1)
        raw_sim = float(similarities[idx])
        score = (rasio * 20) + (absolute * 50) + (max(0.0, raw_sim) * 30)

        print(f"{'='*50}")
        print(f"Career         : {row['career']}")
        print(f"Career Skills  : {sorted(c_skills)}")
        print(f"Matched Skills : {sorted(matched)}")
        print(f"matched_count  : {matched_count} / {total} career skills")
        print(f"rasio_match    : {rasio:.4f} → {rasio*20:.2f} poin (bobot 20%)")
        print(f"absolute_match : {absolute:.4f} → {absolute*50:.2f} poin (bobot 50%)")
        print(f"raw_sim        : {raw_sim:.4f} → {max(0.0,raw_sim)*30:.2f} poin (bobot 30%)")
        print(f"FINAL SCORE    : {score:.2f}\n")
