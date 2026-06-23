import pandas as pd
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import re
from collections import Counter


data = pd.read_csv("data/processed/career_profiles.csv")
data

def clean_title(title):
    title = title.split("-")[0]

    title = re.sub(
        r"\b(entry level|entry-level|junior|senior|intern|trainee|fresher|experienced)\b",
        "",
        title,
        flags=re.IGNORECASE
    )

    title = re.sub(r"\s+", " ", title).strip()

    return title

data["Title_Clean"] = data["Title"].apply(clean_title)

def combine_unique_skills(series):
    skills = set()

    for row in series.dropna():
        for skill in str(row).split(";"):
            skill = skill.strip()
            if skill:
                skills.add(skill)

    return "; ".join(sorted(skills))

data_grouped = (
    data.groupby("Title_Clean", as_index=False)
        .agg({
            "Skills": combine_unique_skills,
            "Keywords": lambda x: " ".join(x.dropna().astype(str)),
            "Responsibilities": lambda x: " ".join(x.dropna().astype(str))
        })
)

data_grouped["job_text"] = (data_grouped["Title_Clean"].fillna("") + " " +
    data_grouped["Skills"].fillna("") + " " +
    data_grouped["Keywords"].fillna("") + " " +
    data_grouped["Responsibilities"].fillna(""))

model = SentenceTransformer("all-MiniLM-L6-v2") #SBERT

def get_core_skills_by_frequency(job_title,original_data,threshold=0.5):

    jobs = original_data[original_data["Title_Clean"].str.lower() == job_title.lower()]
    total_jobs = len(jobs)

    if total_jobs == 0:
        return set()

    skill_counter = Counter()

    for skills in jobs["Skills"]:
        skill_list = [
            s.strip().lower()
            for s in str(skills)
            .replace(";", ",")
            .split(",")
            if s.strip()]

        for skill in set(skill_list):
            skill_counter[skill] += 1

    core_skills = {
        skill
        for skill, count in skill_counter.items()
        if count / total_jobs >= threshold
    }

    return core_skills

def analyze_selected_job(user_input_text,selected_job_title,data_df,model_encoder):

    user_input_text = user_input_text.lower()

    #cari job
    job_row_df = data_df[data_df["Title_Clean"].str.lower()== selected_job_title.lower()]

    if job_row_df.empty:
        return {"error":f"Job '{selected_job_title}' not found."}

    job_row = job_row_df.iloc[0]

    #semantic match
    user_emb = model_encoder.encode([user_input_text])[0]
    job_emb = model.encode([job_row["job_text"]])[0]
    semantic_score = cosine_similarity([user_emb],[job_emb])[0][0]
    semantic_score = round(semantic_score * 100,2)

    #core skills
    job_skills = get_core_skills_by_frequency(
        selected_job_title,
        data,          #dataset asli
        threshold=0.5)  #bisa diubah

    #User skill
    user_skills = [s.strip().lower()
        for s in user_input_text.split(",")
        if s.strip()]

    #SBERT
    matched_skills = []

    if len(user_skills) > 0 and len(job_skills) > 0:
        job_skills_list = list(job_skills)
        job_embs = model_encoder.encode(job_skills_list)
        user_embs = model_encoder.encode(user_skills)

        for i, job_skill in enumerate(job_skills_list):
            sims = cosine_similarity([job_embs[i]],user_embs)[0]
            best_similarity = max(sims)
            if best_similarity >= 0.7:  #treshold SBERT u/ mencocokkan skill
                matched_skills.append(job_skill)
    missing_skills = sorted(list(set(job_skills) - set(matched_skills)))
    #kalkulasi skor kesiapan(readiness score)
    total_skills_count = len(job_skills)
    matched_skills_count = len(matched_skills)

    # Antisipasi jika di database pekerjaan tersebut tidak mencantumkan skill sama sekali
    if total_skills_count > 0:
        readiness_score = (matched_skills_count / total_skills_count) * 100
    else:
        readiness_score = 0.0

    gap_percentage = 100.0 - readiness_score
    
    return {
        "job": selected_job_title,
        "semantic_match":f"{semantic_score:.2f}%",
        "matched_skills":sorted(matched_skills),
        "missing_skills":missing_skills,
        "readiness_score":f"{readiness_score:.2f}%",
        "gap_percentage":f"{gap_percentage:.2f}%"}

user_input = "python, hadoop"
selected_job = "Data Analyst"
result = analyze_selected_job(user_input, selected_job, data_grouped, model)
result