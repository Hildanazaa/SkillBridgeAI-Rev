import os
import re
import json
import logging
import warnings
import getpass
from collections import Counter

import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer
import google.generativeai as genai

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

API_KEY = os.getenv("GOOGLE_API_KEY")
if not API_KEY:
    raise RuntimeError("GOOGLE_API_KEY environment variable must be set.")
genai.configure(api_key=API_KEY)


def clean_title(title: str) -> str:
    title = str(title).split("-")[0]
    title = re.sub(
        r"\b(entry level|entry-level|junior|senior|intern|trainee|fresher|experienced)\b",
        "",
        title,
        flags=re.IGNORECASE
    )
    return re.sub(r"\s+", " ", title).strip()


def combine_unique_skills(series: pd.Series) -> str:
    skills = set()
    for row in series.dropna():
        for skill in str(row).replace(";", ",").split(","):
            skill = skill.strip()
            if skill:
                skills.add(skill)
    return "; ".join(sorted(skills))


def get_core_skills_by_frequency(job_title: str, original_data: pd.DataFrame, threshold: float = 0.5) -> set:
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


def prepare_and_embed_dataset(input_csv: str):
    print("Memuat dan membersihkan dataset pekerjaan...")
    data = pd.read_csv(input_csv)
    data["Title_Clean"] = data["Title"].apply(clean_title)
    
    data_grouped = data.groupby("Title_Clean", as_index=False).agg({
        "Skills": combine_unique_skills,
        "Keywords": lambda x: " ".join(x.dropna().astype(str)),
        "Responsibilities": lambda x: " ".join(x.dropna().astype(str))
    })
    
    data_grouped["job_text"] = (
        data_grouped["Title_Clean"].fillna("") + " " +
        data_grouped["Skills"].fillna("") + " " +
        data_grouped["Keywords"].fillna("") + " " +
        data_grouped["Responsibilities"].fillna("")
    )
    
    print("Memuat SBERT Model (all-MiniLM-L6-v2) untuk kalkulasi embedding...")
    model = SentenceTransformer("all-MiniLM-L6-v2")
    
    print("Menghasilkan representasi matriks embedding data pekerjaan...")
    embeddings_array = model.encode(
        data_grouped["job_text"].tolist(),
        show_progress_bar=True,
        convert_to_numpy=True
    )
    
    os.makedirs("data/processed", exist_ok=True)
    os.makedirs("data/embeddings", exist_ok=True)
    
    data_grouped.to_csv("data/processed/career_profiles.csv", index=False)
    np.save("data/embeddings/career_embeddings.npy", embeddings_array)
    print("asil prapemrosesan data & embedding berhasil disimpan.")
    
    return data, data_grouped, model, embeddings_array


def analyze_selected_job(user_input_text: str, selected_job_title: str, original_data: pd.DataFrame, data_grouped: pd.DataFrame, model_encoder: SentenceTransformer):
    user_input_text = user_input_text.lower()
    job_row_df = data_grouped[data_grouped["Title_Clean"].str.lower() == selected_job_title.lower()]

    if job_row_df.empty:
        return {"success": False, "error": f"Job '{selected_job_title}' tidak ditemukan di database."}

    job_row = job_row_df.iloc[0]

    user_emb = model_encoder.encode([user_input_text])[0]
    job_emb = model_encoder.encode([job_row["job_text"]])[0]
    semantic_score = round(cosine_similarity([user_emb], [job_emb])[0][0] * 100, 2)

    job_skills = get_core_skills_by_frequency(selected_job_title, original_data, threshold=0.5)
    user_skills = [s.strip().lower() for s in user_input_text.split(",") if s.strip()]

    matched_skills = []
    if user_skills and job_skills:
        job_skills_list = list(job_skills)
        job_embs = model_encoder.encode(job_skills_list)
        user_embs = model_encoder.encode(user_skills)

        for i, job_skill in enumerate(job_skills_list):
            sims = cosine_similarity([job_embs[i]], user_embs)[0]
            if max(sims) >= 0.5:  # Batas ambang SBERT pencocokan kemiripan skill
                matched_skills.append(job_skill)
                
    missing_skills = sorted(list(set(job_skills) - set(matched_skills)))

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
        "readiness_score": f"{readiness_score:.2f}%",
        "gap_percentage": f"{gap_percentage:.2f}%"
    }


def generate_roadmap_json(user_skills: str, job_title: str, missing_skills: str, gap_percentage: str, readiness_score: str) -> str:
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
    1. DURASI MAKSIMAL 4 MINGGU: Rencana belajar HANYA boleh berkisar antara 1 sampai maksimal 4 minggu (W1 sampai W4). Tidak boleh membuat W5 ke atas!
    2. KONDISI GAP BESAR (Jika Gap Percentage > 50%): Jangan paksakan memasukkan semua 'missing_skills' ke dalam 4 minggu karena tidak realistis. Pilih 2-3 skill fondasi yang paling krusial saja untuk dipelajari di Fase 1 (W1-W4) ini. Masukkan pesan edukasi di dalam field "note" agar pengguna fokus ke dasar dulu dan diarahkan untuk melakukan input ulang skill bulan depan setelah fase ini selesai.
    3. KONDISI GAP KECIL (Jika Gap Percentage <= 20%): Jangan mengada-ada materi sampai 4 minggu. Buat kurikulum pendek saja (misal hanya W1 saja, atau W1 dan W2) untuk menambal sedikit skill yang kurang tersebut. Jika W3 atau W4 tidak diperlukan, isi objek minggunya dengan null (contoh: "W3": null, "W4": null).

    INSTRUKSI FORMAT OUTPUT:
    Keluarkan HASILNYA HANYA berupa JSON valid dengan struktur di bawah ini. Jangan berikan markdown backticks (```json), teks pembuka, atau penutup di luar JSON.
    Gunakan Bahasa Indonesia yang profesional dan solutif.

    STRUKTUR JSON YANG DIWAJIBKAN:
    {{
      "skill_gap_analysis": [
        "Analisis kritis 1 mengenai gap skill pengguna berdasarkan data input",
        "Analisis kritis 2 mengenai langkah strategis fase ini"
      ],
     "roadmap": {{
        "W1": {{
          "tag": "Fokus Topik Utama Minggu 1",
          "title": "Judul Pembelajaran Minggu 1",
          "d1": {{ "title": "Topik Hari 1", "desc": "Aktivitas belajar Hari 1", "resources": [{{ "title": "Baca Tutorial di Google", "link": "[https://www.google.com/search?q=tutorial](https://www.google.com/search?q=tutorial)+[MASUKKAN_TOPIK_HARI_1_DI_SINI]+bahasa+indonesia" }}, {{ "title": "Tonton Video di YouTube", "link": "[https://www.youtube.com/results?search_query=tutorial](https://www.youtube.com/results?search_query=tutorial)+[MASUKKAN_TOPIK_HARI_1_DI_SINI]+bahasa+indonesia" }}] }},
          "d2": {{ "title": "Topik Hari 2", "desc": "Aktivitas belajar Hari 2", "resources": [{{ "title": "Baca Tutorial di Google", "link": "[https://www.google.com/search?q=tutorial](https://www.google.com/search?q=tutorial)+[MASUKKAN_TOPIK_HARI_2_DI_SINI]+bahasa+indonesia" }}, {{ "title": "Tonton Video di YouTube", "link": "[https://www.youtube.com/results?search_query=tutorial](https://www.youtube.com/results?search_query=tutorial)+[MASUKKAN_TOPIK_HARI_2_DI_SINI]+bahasa+indonesia" }}] }}
        }}
      }},
      "note": "Tulis catatan edukasi/motivasi kustom di sini."
    }}
    """

    response = model.generate_content(
        prompt_template,
        generation_config={"response_mime_type": "application/json", "temperature": 0.2}
    )

    if response and response.text:
        return response.text
    else:
        return json.dumps({"error": "Gemini model failed to generate a roadmap."})


if __name__ == "__main__":
    dataset_path = "job_dataset_cleaned.csv" 
    
    if os.path.exists(dataset_path):
        data_raw, data_grouped, model, embeddings = prepare_and_embed_dataset(dataset_path)
    else:
        # print(f"File {dataset_path} tidak ditemukan. Pastikan file dataset sudah disiapkan.")
        exit()

    user_input = "excel, python, git, matplotlib"
    selected_job = "Fintech Engineer"
    
    print(f"\n🔍 Melakukan analisis gap untuk Posisi: '{selected_job}' berdasarkan keahlian pengguna...")
    analysis_result = analyze_selected_job(user_input, selected_job, data_raw, data_grouped, model)
    
    if not analysis_result["success"]:
        print(analysis_result["error"])
        exit()

    print("✅ Analisis Kesiapan Karir Berhasil:")
    print(f"   - Semantic Match Score : {analysis_result['semantic_match']}")
    print(f"   - Readiness Score      : {analysis_result['readiness_score']}")
    print(f"   - Skill yang COCOK     : {analysis_result['matched_skills']}")
    print(f"   - Skill yang KURANG    : {analysis_result['missing_skills']}")

    matched_skills_str = ", ".join(analysis_result['matched_skills']) if analysis_result['matched_skills'] else "Tidak ada"
    missing_skills_str = ", ".join(analysis_result['missing_skills']) if analysis_result['missing_skills'] else "Tidak ada"
    
    print("\n🤖 Gemini sedang menyusun kurikulum JSON adaptif (Iterative)...")
    print("-" * 70)

    try:
        json_output_raw = generate_roadmap_json(
            user_skills=matched_skills_str,
            job_title=analysis_result['job'],
            missing_skills=missing_skills_str,
            gap_percentage=analysis_result['gap_percentage'],
            readiness_score=analysis_result['readiness_score']
        )

        # Parsing string menjadi objek JSON Python agar valid
        data_roadmap = json.loads(json_output_raw)

        # print("BERHASIL! Kurikulum berhasil dikemas ke dalam struktur JSON:")
        print(json.dumps(data_roadmap, indent=2, ensure_ascii=False))

        # Ekspor berkas final
        with open('roadmap_result.json', 'w', encoding='utf-8') as f:
            json.dump(data_roadmap, f, indent=2, ensure_ascii=False)
        print("\n💾 Berkas 'roadmap_result.json' sukses diperbarui! Siap dikonsumsi sistem Frontend.")

    except Exception as e:
        print(f"Terjadi kendala teknis saat memproses prompt Gemini. Detail: {e}")