import json
import os
import re
import warnings
import logging
from pathlib import Path
from collections import Counter
from typing import Dict, List, Any
import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer
import google.generativeai as genai

# SETUP & CONFIGURATION
warnings.filterwarnings("ignore")
os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"
os.environ["HF_HUB_DISABLE_IMPLICIT_TOKEN_WARNING"] = "1"
os.environ["HF_HUB_OFFLINE"] = "1"
os.environ["TRANSFORMERS_OFFLINE"] = "1"

try:
    from huggingface_hub.utils import disable_progress_bars
    disable_progress_bars()
except ImportError:
    pass

logging.getLogger("sentence_transformers").setLevel(logging.WARNING)
logging.getLogger("transformers").setLevel(logging.ERROR)

# Configure Gemini API from environment only
API_KEY = os.getenv("GOOGLE_API_KEY")
if not API_KEY:
    raise RuntimeError("GOOGLE_API_KEY environment variable must be set.")
genai.configure(api_key=API_KEY)

BASE_DIR = Path(__file__).resolve().parent.parent
DATASET_PATH = BASE_DIR / "job_dataset_cleaned.csv"
DATA_DIR = BASE_DIR / "FinalProject" / "data"

# Global cache
_model = None
_data_raw = None
_data_grouped = None
_embeddings = None


# ==========================================
# HELPER FUNCTIONS
# ==========================================
def clean_title(title: str) -> str:
    """Membersihkan level posisi/jabatan dari judul pekerjaan."""
    title = str(title).split("-")[0]
    title = re.sub(
        r"\b(entry level|entry-level|junior|senior|intern|trainee|fresher|experienced)\b",
        "",
        title,
        flags=re.IGNORECASE
    )
    return re.sub(r"\s+", " ", title).strip()


def combine_unique_skills(series: pd.Series) -> str:
    """Menggabungkan kumpulan string skill menjadi daftar unik."""
    skills = set()
    for row in series.dropna():
        for skill in str(row).replace(";", ",").split(","):
            skill = skill.strip()
            if skill:
                skills.add(skill)
    return "; ".join(sorted(skills))


def get_core_skills_by_frequency(job_title: str, original_data: pd.DataFrame, threshold: float = 0.5) -> set:
    """Mendapatkan keahlian inti yang sering muncul pada suatu posisi."""
    jobs = original_data[original_data["Title_Clean"].str.lower() == job_title.lower()]
    total_jobs = len(jobs)
    if total_jobs == 0:
        return set()

    skill_counter = Counter()
    for skills in jobs["Skills"]:
        skill_list = [s.strip().lower() for s in str(skills).replace(";", ",").split(",") if s.strip()]
        for skill in set(skill_list):
            skill_counter[skill] += 1

    return {skill for skill, count in skill_counter.items() if (count / total_jobs) >= threshold}


# DATA LOADING & INITIALIZATION
def initialize_dataset():
    """Load dan cache dataset sekali saja."""
    global _model, _data_raw, _data_grouped, _embeddings
    
    if _model is not None:
        return _model, _data_raw, _data_grouped, _embeddings
    
    if not os.path.exists(DATASET_PATH):
        raise FileNotFoundError(f"Dataset tidak ditemukan: {DATASET_PATH}")
    
    # Load dataset
    _data_raw = pd.read_csv(DATASET_PATH)
    _data_raw["Title_Clean"] = _data_raw["Title"].apply(clean_title)
    
    # Group dan aggregate
    _data_grouped = _data_raw.groupby("Title_Clean", as_index=False).agg({
        "Skills": combine_unique_skills,
        "Keywords": lambda x: " ".join(x.dropna().astype(str)),
        "Responsibilities": lambda x: " ".join(x.dropna().astype(str))
    })
    
    # Combine text untuk embedding
    _data_grouped["job_text"] = (
        _data_grouped["Title_Clean"].fillna("") + " " +
        _data_grouped["Skills"].fillna("") + " " +
        _data_grouped["Keywords"].fillna("") + " " +
        _data_grouped["Responsibilities"].fillna("")
    )
    
    # Load model
    _model = SentenceTransformer("all-MiniLM-L6-v2")
    
    # Generate embeddings
    _embeddings = _model.encode(
        _data_grouped["job_text"].tolist(),
        show_progress_bar=False,
        convert_to_numpy=True
    )
    
    return _model, _data_raw, _data_grouped, _embeddings


# SKILL GAP ANALYSIS
def analyze_selected_job(user_input_text: str, selected_job_title: str) -> Dict[str, Any]:
    """Membandingkan input keahlian user dengan target pekerjaan."""
    model, data_raw, data_grouped, embeddings = initialize_dataset()
    
    user_input_text = user_input_text.lower()
    job_row_df = data_grouped[data_grouped["Title_Clean"].str.lower() == selected_job_title.lower()]

    if job_row_df.empty:
        return {"success": False, "error": f"Job '{selected_job_title}' tidak ditemukan."}

    job_row = job_row_df.iloc[0]

    # Semantic similarity score
    user_emb = model.encode([user_input_text])[0]
    job_emb = model.encode([job_row["job_text"]])[0]
    semantic_score = round(cosine_similarity([user_emb], [job_emb])[0][0] * 100, 2)

    # Get core skills
    job_skills = get_core_skills_by_frequency(selected_job_title, data_raw, threshold=0.5)
    user_skills = [s.strip().lower() for s in user_input_text.split(",") if s.strip()]

    matched_skills = []
    if user_skills and job_skills:
        job_skills_list = list(job_skills)
        job_embs = model.encode(job_skills_list)
        user_embs = model.encode(user_skills)

        for i, job_skill in enumerate(job_skills_list):
            sims = cosine_similarity([job_embs[i]], user_embs)[0]
            if max(sims) >= 0.5:
                matched_skills.append(job_skill)
                
    missing_skills = sorted(list(set(job_skills) - set(matched_skills)))

    # Calculate metrics
    total_skills_count = len(job_skills)
    matched_skills_count = len(matched_skills)
    readiness_score = (matched_skills_count / total_skills_count) * 100 if total_skills_count > 0 else 0.0
    gap_percentage = 100.0 - readiness_score

    return {
        "success": True,
        "job": selected_job_title,
        "semantic_match": f"{semantic_score:.2f}%",
        "total_required_skills": total_skills_count,
        "matched_skills_count": matched_skills_count,
        "matched_skills": sorted(matched_skills),
        "missing_skills": missing_skills,
        "readiness_score": int(readiness_score),
        "gap_percentage": f"{gap_percentage:.2f}%",
        "owned_skills": sorted(matched_skills),
        "missing_skills_priority": [{"skill": s} for s in missing_skills]
    }


# ROADMAP GENERATION
def generate_roadmap_json(user_skills: str, job_title: str, missing_skills: str, gap_percentage: str, readiness_score: str) -> str:
    """Generate roadmap dengan Gemini AI."""
    model = genai.GenerativeModel('gemini-2.5-flash')

    prompt_template = f"""
Kamu adalah seorang Expert IT Curriculum Developer dan Career Mentor. Tugasmu adalah menganalisis kesenjangan keterampilan (skill gap)
dan menyusun rencana pembelajaran dalam format JSON menggunakan metode "Iterative Learning" (Maksimal 4 Minggu) untuk menutup gap tersebut.

DATA INPUT UTAMA:
- Posisi Target: {job_title}
- Keterampilan Pengguna Saat Ini: {user_skills}
- Keterampilan yang Kurang (Missing Skills): {missing_skills}
- Skor Kesiapan (Readiness Score): {readiness_score}
- Skor Ketertinggalan (Gap Percentage): {gap_percentage}

ATURAN ADAPTIF LOGIKA BISNIS (WAJIB DIPATUHI):
1. DURASI MAKSIMAL 4 MINGGU
2. KONDISI GAP BESAR (Jika Gap Percentage > 50%): Pilih 2-3 skill fondasi saja untuk dipelajari di Fase 1 (W1-W4)
3. KONDISI GAP KECIL (Jika Gap Percentage <= 20%): Buat kurikulum pendek, isi null untuk minggu yang tidak diperlukan

INSTRUKSI FORMAT OUTPUT:
Keluarkan HASILNYA HANYA berupa JSON valid. Jangan berikan markdown backticks atau teks di luar JSON.

STRUKTUR JSON YANG DIWAJIBKAN:
{{
  "weeks": [
    {{
      "week": 1,
      "focus": "Fokus Topik Utama Minggu 1",
      "title": "Judul Pembelajaran Minggu 1",
      "days": [
        {{
          "day": 1,
          "topic": "Topik Hari 1",
          "detail": "Deskripsi detail aktivitas belajar",
          "resource": "Nama Resource",
          "resource_url": "https://google.com"
        }}
      ]
    }}
  ],
  "note": "Catatan motivasi dan rekomendasi"
}}
"""

    response = model.generate_content(
        prompt_template,
        generation_config={"response_mime_type": "application/json", "temperature": 0.2}
    )

    if response and response.text:
        return response.text
    else:
        return json.dumps({"error": "Gemini failed"})


# ==========================================
# PUBLIC API FUNCTIONS
# ==========================================
def get_recommendations(user_text: str):
    """Return list of recommended jobs based on user skills."""
    model, data_raw, data_grouped, embeddings = initialize_dataset()
    
    user_emb = model.encode([user_text])[0]
    scores = cosine_similarity([user_emb], embeddings)[0]
    
    top_indices = np.argsort(scores)[::-1][:5]
    
    recommendations = []
    for idx in top_indices:
        job_title = data_grouped.iloc[idx]["Title_Clean"]
        match_score = float(scores[idx])
        
        recommendations.append({
            "title": job_title,
            "match_score": match_score,
            "experience_level": "Entry Level",
            "missing_skills": []
        })
    
    return {"recommendations": recommendations}


def get_analysis(user_text: str, target_title: str):
    """Return skill gap analysis for selected job."""
    result = analyze_selected_job(user_text, target_title)
    
    if not result["success"]:
        return {"error": result["error"]}
    
    return {
        "readiness_score": result["readiness_score"],
        "owned_skills": result["owned_skills"],
        "missing_skills_priority": result["missing_skills_priority"]
    }


def get_roadmap(target_title: str, missing_skills: list):
    """Return personalized learning roadmap."""
    missing_str = ", ".join(missing_skills) if missing_skills else "Tidak ada"
    
    json_output = generate_roadmap_json(
        user_skills="User skills",
        job_title=target_title,
        missing_skills=missing_str,
        gap_percentage="25%",
        readiness_score="75%"
    )
    
    try:
        roadmap_data = json.loads(json_output)
        return roadmap_data
    except:
        return {"weeks": [], "note": "Gagal generate roadmap"}
