import os
import logging
import warnings
import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

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

from sentence_transformers import SentenceTransformer

import json
from src.skill_extraction.skill_gap import normalize_skill_name

# Load career profiles and precomputed embeddings
_raw_careers = pd.read_csv("data/processed/career_profiles.csv")
_raw_embeddings = np.load("data/embeddings/career_embeddings.npy")

# Filter out careers with 0 skills in career_skills.json and populate career_to_skills mapping
career_to_skills = {}
try:
    with open("data/processed/career_skills.json", "r", encoding="utf-8") as f:
        _skills_data = json.load(f)
    _valid_careers = {item["career"] for item in _skills_data if len(item.get("skills", [])) > 0}
    _valid_indices = [i for i, r in _raw_careers.iterrows() if r["career"] in _valid_careers]
    
    careers = _raw_careers.iloc[_valid_indices].reset_index(drop=True)
    embeddings = _raw_embeddings[_valid_indices]
    career_to_skills = {item["career"]: item.get("skills", []) for item in _skills_data}
except Exception:
    careers = _raw_careers
    embeddings = _raw_embeddings

_model = None

def get_model():
    global _model
    if _model is None:
        _model = SentenceTransformer("all-MiniLM-L6-v2")
    return _model


def get_career_description(career_name: str) -> str:
    c = career_name.lower()
    
    # IT & Software Engineering
    if "senior" in c:
        return "Insinyur perangkat lunak senior yang bertanggung jawab atas arsitektur sistem, memimpin tim pengembang, serta merancang solusi teknis kompleks yang scalable."
    if "backend" in c:
        return "Bertanggung jawab untuk membangun dan memelihara arsitektur server, basis data (database), serta logika aplikasi di balik layar (server-side)."
    if "frontend" in c:
        return "Fokus pada pengembangan bagian visual, tata letak, dan elemen interaktif aplikasi atau website yang langsung berinteraksi dengan pengguna (client-side)."
    if "fullstack" in c or "full stack" in c:
        return "Menguasai pengembangan frontend (sisi klien) dan backend (sisi server) untuk membangun aplikasi secara utuh dan terintegrasi."
    if "android" in c:
        return "Merancang, mengembangkan, dan memelihara aplikasi mobile yang berjalan khusus pada sistem operasi Android."
    if "ios" in c:
        return "Merancang, mengembangkan, dan memelihara aplikasi mobile yang berjalan khusus pada sistem operasi iOS (Apple)."
    if "mobile" in c:
        return "Mengembangkan aplikasi mobile lintas platform (cross-platform) atau native untuk perangkat ponsel pintar dan tablet."
    if "flutter" in c:
        return "Mengembangkan aplikasi mobile lintas platform (Android dan iOS) menggunakan SDK Flutter dan bahasa Dart."
    if "java developer" in c or "java programmer" in c:
        return "Spesialis pengembang perangkat lunak menggunakan bahasa pemrograman Java untuk membangun sistem enterprise skala besar dan API."
    if "php developer" in c or "php programmer" in c:
        return "Spesialis pengembang web menggunakan bahasa pemrograman PHP untuk membangun backend website dinamis dan integrasi database."
    if "golang" in c:
        return "Mengembangkan microservices dan sistem backend berkinerja tinggi menggunakan bahasa pemrograman Go (Golang)."
    if "ui/ux" in c or "ui ux" in c:
        return "Merancang antarmuka pengguna (UI) yang estetis dan merancang pengalaman pengguna (UX) yang intuitif dan ramah pengguna."
    if "qa" in c or "quality assurance" in c:
        return "Memastikan kualitas perangkat lunak dengan melakukan pengujian berkala, mendeteksi bug, dan memverifikasi kesesuaian fitur sebelum dirilis."
    if "devops" in c or "cloud" in c:
        return "Mengintegrasikan proses pengembangan (development) dengan operasional infrastruktur cloud, otomatisasi CI/CD, dan pemeliharaan server."
    if "database" in c:
        return "Mengelola, merancang, mengamankan, dan mengoptimalkan performa sistem basis data organisasi untuk efisiensi penyimpanan data."
    if "network" in c:
        return "Merancang, mengonfigurasi, dan memelihara infrastruktur jaringan komputer dan keamanan sistem komunikasi data organisasi."
    if "security" in c:
        return "Melindungi aset digital, sistem informasi, dan jaringan organisasi dari ancaman serangan siber, kebocoran data, dan akses ilegal."
    if "architect" in c:
        return "Merancang cetak biru arsitektur sistem IT atau bangunan fisik secara menyeluruh agar kokoh, efisien, dan sesuai standar industri."
    if "web developer" in c:
        return "Mengembangkan dan memelihara aplikasi web, memastikan performa dan integrasi yang baik antara komponen frontend dan backend."
    if "web programmer" in c:
        return "Menulis kode pemrograman web dan mengimplementasikan logika teknis untuk membuat aplikasi dan situs web berjalan dengan dinamis."
    if "software developer" in c or "software engineer" in c or "developer" in c or "programmer" in c:
        return "Merancang, menulis, dan menguji kode program untuk membangun aplikasi desktop, mobile, atau sistem perangkat lunak yang andal."

    # Data
    if "data scientist" in c:
        return "Menganalisis data bervolume besar menggunakan algoritma machine learning dan statistika untuk memprediksi tren dan membuat pemodelan keputusan."
    if "data engineer" in c:
        return "Membangun dan memelihara saluran pipa data (data pipeline) serta infrastruktur untuk pengolahan data skala besar."
    if "data analyst" in c or "analytics" in c:
        return "Mengolah, membersihkan, dan memvisualisasikan data untuk memberikan wawasan (insight) bisnis yang mendukung pengambilan keputusan."

    # Product & Project Management
    if "project manager" in c or "project coordinator" in c:
        return "Merencanakan, memimpin, mengoordinasikan, dan mengevaluasi pelaksanaan proyek agar selesai tepat waktu dan sesuai anggaran."
    if "product manager" in c or "product owner" in c:
        return "Mengembangkan visi produk, menyusun strategi fitur, dan menjembatani tim bisnis, desainer, serta engineer untuk kesuksesan produk."
    if "scrum master" in c:
        return "Memfasilitasi tim pengembang dalam menerapkan metodologi Agile/Scrum untuk meningkatkan produktivitas dan kolaborasi."

    # Marketing & Creative
    if "digital marketing" in c:
        return "Merencanakan dan menjalankan strategi pemasaran online melalui media sosial, iklan berbayar (Ads), SEO, dan kampanye email."
    if "writer" in c or "editor" in c or "copywriter" in c:
        return "Membuat, menyunting, dan menyusun konten teks atau media kreatif untuk keperluan publikasi, pemasaran, atau dokumentasi teknis."
    if "social media" in c:
        return "Mengelola konten, interaksi audiens, dan kampanye promosi di berbagai platform media sosial resmi organisasi."
    if "graphic designer" in c or "design grafis" in c or "designer" in c or "arsitek" in c:
        return "Membuat konsep komunikasi visual, ilustrasi, tata letak, atau desain estetis untuk keperluan promosi, branding, atau produk."
    if "marketing" in c:
        return "Menyusun kampanye promosi, menganalisis pasar, dan mengoordinasikan aktivitas branding untuk meningkatkan brand awareness produk."

    # Sales & Business Development
    if "sales" in c or "salesman" in c or "salesperson" in c or "canvasser" in c:
        return "Melakukan pendekatan kepada calon pelanggan, mempresentasikan produk, dan melakukan penjualan langsung untuk mencapai target bisnis."
    if "business development" in c or "acquisition" in c or "relationship officer" in c or "relationship manager" in c:
        return "Membangun kemitraan strategis, mencari peluang pasar baru, dan memelihara hubungan baik dengan klien untuk pertumbuhan bisnis jangka panjang."
    if "account executive" in c or "account officer" in c:
        return "Menjadi penghubung utama antara klien dan perusahaan untuk mengelola portofolio proyek dan memastikan kepuasan pelanggan."

    # Finance & Accounting
    if "accounting" in c or "accountant" in c:
        return "Mencatat transaksi keuangan bulanan, menyusun laporan neraca/laba-rugi, dan memastikan kepatuhan standar akuntansi."
    if "tax" in c or "pajak" in c:
        return "Mengelola pelaporan, penghitungan, penyetoran, dan perencanaan kewajiban pajak perusahaan agar sesuai dengan regulasi pemerintah."
    if "finance" in c or "financial" in c or "treasury" in c:
        return "Mengatur arus kas (cashflow), mengelola anggaran pengeluaran, serta merencanakan strategi pembiayaan dan investasi perusahaan."
    if "auditor" in c or "audit" in c:
        return "Memeriksa dan mengevaluasi laporan keuangan serta proses operasional untuk mendeteksi kecurangan dan memastikan kepatuhan regulasi."

    # Human Resources & Administration
    if "hr" in c or "human resources" in c or "hrd" in c or "recruitment" in c or "recruiter" in c:
        return "Mengelola siklus SDM mulai dari rekrutmen karyawan baru, pelatihan, penggajian (payroll), hingga hubungan industrial karyawan."
    if "legal" in c:
        return "Menangani dokumen kontrak hukum, memberikan nasihat hukum, dan memastikan seluruh kepatuhan operasional terhadap undang-undang."
    if "admin" in c or "administration" in c or "sekretaris" in c or "secretary" in c or "clerk" in c:
        return "Mengelola tugas-tugas administratif harian, surat-menyurat, pengarsipan dokumen, dan koordinasi operasional kantor."

    # Engineering & Technical (Non-IT)
    if "civil engineer" in c or "construction" in c:
        return "Merancang, mengawasi, dan mengelola pembangunan infrastruktur fisik seperti gedung, jembatan, jalan, dan sistem air."
    if "electrical engineer" in c or "listrik" in c:
        return "Merancang, memelihara, dan memperbaiki sistem kelistrikan, instrumentasi kontrol, serta perangkat elektronik industri."
    if "mechanical" in c or "mekanik" in c or "technician" in c or "teknisi" in c:
        return "Melakukan perawatan preventif, perbaikan mesin, dan penyelesaian kendala teknis pada peralatan mekanis atau otomotif."
    if "engineer" in c:
        return "Menerapkan prinsip sains dan matematika untuk merancang, memecahkan masalah teknis, dan mengoptimalkan sistem industri."

    # Operations & Service
    if "customer service" in c or "customer relation" in c or "call center" in c or "telesales" in c or "receptionist" in c or "front office" in c:
        return "Melayani pertanyaan pelanggan, menangani keluhan, memberikan solusi produk, dan memastikan kepuasan pelanggan secara profesional."
    if "warehouse" in c or "gudang" in c or "logistics" in c or "purchasing" in c or "procurement" in c or "supply chain" in c:
        return "Mengelola arus penerimaan dan pengeluaran barang di gudang, kontrol inventaris, serta pengadaan kebutuhan inventaris operasional."
    if "chef" in c or "cook" in c or "pastry" in c or "kitchen" in c:
        return "Menyiapkan bahan makanan, merancang menu, memasak hidangan berkualitas tinggi, dan menjaga kebersihan area dapur."
    if "waiter" in c or "waitress" in c or "steward" in c or "f&b" in c or "food" in c:
        return "Melayani pemesanan makanan dan minuman, mengantarkan hidangan, serta memastikan kenyamanan tamu di restoran atau kafe."
    if "housekeeping" in c or "clean" in c or "laundry" in c:
        return "Menjaga kebersihan, kerapian, dan keindahan kamar hotel, ruangan kantor, atau area publik demi kenyamanan penghuni."

    # Education & Healthcare
    if "teacher" in c or "guru" in c or "pendidik" in c or "instructor" in c:
        return "Merencanakan materi pembelajaran, mengajar kelas didik, melakukan evaluasi belajar, dan membimbing tumbuh kembang siswa."
    if "nurse" in c or "perawat" in c or "dokter" in c or "medical" in c or "therapist" in c or "apoteker" in c:
        return "Memberikan pelayanan asuhan keperawatan atau medis kepada pasien, mengelola obat-obatan, dan membantu pemulihan kesehatan."

    # Fallback
    return f"Posisi profesional yang bertanggung jawab atas pengelolaan, pelaksanaan tugas, dan koordinasi terkait bidang {career_name}."


def recommend_career(user_skill_text: str, top_k: int = 5):
    user_skills_list = [s.strip() for s in user_skill_text.split(",") if s.strip()]
    if not user_skills_list:
        return {
            "success": False,
            "message": "Masukkan minimal 1 skill"
        }
    
    # 1. Aligned query formatting
    aligned_query = "The candidate is proficient and has skills in: " + ", ".join(user_skills_list) + "."
    
    # 2. Get user embedding
    user_embedding = get_model().encode([aligned_query])

    # 3. Calculate semantic cosine similarity
    similarities = cosine_similarity(
        user_embedding,
        embeddings
    )[0]

    recommendations = []
    normalized_user = {normalize_skill_name(s) for s in user_skills_list}

    # 4. Score calculation & mapping
    for idx, row in careers.iterrows():
        career_name = row["career"]
        
        # Verify that this specific career has at least one skill matching the user's skills
        c_skills = {normalize_skill_name(s) for s in career_to_skills.get(career_name, [])}
        if len(normalized_user.intersection(c_skills)) == 0:
            continue  # Skip careers that don't match any of the user's skills

        # Calibrate raw similarity to user-friendly 0-100 score range
        raw_sim = float(similarities[idx])
        if raw_sim >= 0.50:
            score = 90.0 + (raw_sim - 0.50) / 0.50 * 10.0
        elif raw_sim >= 0.20:
            score = 20.0 + (raw_sim - 0.20) / 0.30 * 70.0
        else:
            score = max(0.0, raw_sim * 100)
        score = float(max(0.0, min(100.0, score)))

        # Suitability threshold based on calibrated score
        if score >= 75.0:
            suitability = "Sangat Cocok (High Suitability)"
            explain_text = f"Sangat direkomendasikan karena memiliki tingkat kesamaan semantik profil latar belakang yang sangat tinggi sebesar {score:.1f}%."
        elif score >= 50.0:
            suitability = "Cocok (Medium Suitability)"
            explain_text = f"Direkomendasikan karena memiliki tingkat kesamaan semantik profil latar belakang yang memadai sebesar {score:.1f}%."
        else:
            suitability = "Kurang Cocok (Low Suitability)"
            explain_text = f"Kurang direkomendasikan karena tingkat kesamaan semantik profil latar belakang yang rendah sebesar {score:.1f}%."

        recommendations.append({
            "career": career_name,
            "score": score,
            "suitability": suitability,
            "explanation": explain_text,
            "description": get_career_description(career_name)
        })

    # Sort recommendations descending by score
    recommendations = sorted(recommendations, key=lambda x: x["score"], reverse=True)

    top_recommendations = []
    for item in recommendations[:top_k]:
        top_recommendations.append({
            "career": item["career"],
            "score": float(item["score"]),
            "suitability": item["suitability"],
            "explanation": item["explanation"],
            "description": item["description"]
        })

    if not top_recommendations:
        return {
            "success": True,
            "recommendations": [],
            "message": "Tidak ada karir yang cocok dengan keahlian Anda di database."
        }

    return {
        "success": True,
        "recommendations": top_recommendations
    }
import os
import warnings
import logging

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

np.save(
    "data/embeddings/career_embeddings.npy",
    embeddings_array
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
import pandas as pd
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import re
from collections import Counter

data = pd.read_csv("job_dataset_cleaned.csv")
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

data[['Title', 'Title_Clean']]

data[data['Title'] != data['Title_Clean']][['Title', 'Title_Clean']]

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
        }))

print('Original Titles from `data` DataFrame:')
display(data['Title'])

print('\nCleaned Titles from `data_grouped` DataFrame:')
display(data_grouped['Title_Clean'])

data_grouped["job_text"] = (data_grouped["Title_Clean"].fillna("") + " " +
    data_grouped["Skills"].fillna("") + " " +
    data_grouped["Keywords"].fillna("") + " " +
    data_grouped["Responsibilities"].fillna(""))

data_grouped['job_text']

pd.set_option('display.max_columns', None)

display(data_grouped['job_text'])

pd.set_option('display.max_colwidth', 500) # Set to a larger number, e.g., 500 characters

display(data_grouped['job_text'])

data["Title_Clean"].nunique()

from collections import Counter

all_skills = []
for skill_list_str in data['Skills'].dropna():
    skills = [s.strip() for s in skill_list_str.split(';') if s.strip()]
    all_skills.extend(skills)

skill_counts = Counter(all_skills)

print('Top 10 Most Frequent Skills:')
for skill, count in skill_counts.most_common(20):
    print(f'- {skill}: {count}')

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

get_core_skills_by_frequency("Fintech Engineer", data)

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
            if best_similarity >= 0.5:  #treshold SBERT u/ mencocokkan skill
                matched_skills.append(job_skill)
    missing_skills = sorted(list(set(job_skills) - set(matched_skills)))

    #readiness score
    total_skills_count = len(job_skills)
    matched_skills_count = len(matched_skills)

    if total_skills_count > 0:
        readiness_score = (matched_skills_count / total_skills_count) * 100
    else:
        readiness_score = 0.0
    gap_percentage = 100.0 - readiness_score

    return {
        "job": selected_job_title,
        "semantic_match": f"{semantic_score:.2f}%",
        "total_required_skills": total_skills_count,
        "matched_skills_count": matched_skills_count,
        "matched_skills": sorted(matched_skills),
        "missing_skills": missing_skills,
        "readiness_score": f"{readiness_score:.2f}%",
        "gap_percentage": f"{gap_percentage:.2f}%"
    }

user_input = "excel, python, git, matplotlib"
selected_job = "Fintech Engineer"
result = analyze_selected_job(user_input, selected_job, data_grouped, model)
result

data_grouped[data_grouped["Title_Clean"] == "Fintech Engineer"]

fintech_engineer_skills_str = data_grouped[data_grouped["Title_Clean"] == "Fintech Engineer"]["Skills"].iloc[0]
fintech_engineer_skills = [s.strip() for s in fintech_engineer_skills_str.split(';') if s.strip()]
num_fintech_engineer_skills = len(fintech_engineer_skills)

print(f"Number of skills for 'Fintech Engineer': {num_fintech_engineer_skills}")

result_from_analysis = analyze_selected_job(user_input, selected_job, data_grouped, model)
print(f"User Input: {user_input}")
print(f"Selected Job: {selected_job}")
print(f"Matched Skills: {result_from_analysis['matched_skills']}")
print(f"Missing Skills: {result_from_analysis['missing_skills']}")



"""# Gen AI"""

!pip install -q -U google-generativeai

import google.generativeai as genai
from google.colab import userdata
import json

import getpass
import os

if "GOOGLE_API_KEY" not in os.environ:
    os.environ["GOOGLE_API_KEY"] = getpass.getpass("Enter your Google AI API key: ")

genai.configure(api_key=os.environ["GOOGLE_API_KEY"])

def generate_roadmap_json(user_skills, job_title, missing_skills, gap_percentage, readiness_score):
    """
    Fungsi untuk menghasilkan roadmap belajar dalam format JSON adaptif maksimal 4 minggu.
    Menggunakan logika bisnis Iterative Learning & Stateless Session.
    """
    # Inisialisasi model
    model = genai.GenerativeModel('gemini-2.5-flash')

    # PROMPT TEMPLATE DENGAN ATURAN ADAPTIF STRUKTUR KETAT
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
          "d1": {{ "title": "Topik Hari 1", "desc": "Aktivitas belajar Hari 1", "resources": [{{ "title": "Baca Tutorial di Google", "link": "https://www.google.com/search?q=tutorial+[MASUKKAN_TOPIK_HARI_1_DI_SINI]+bahasa+indonesia" }}, {{ "title": "Tonton Video di YouTube", "link": "https://www.youtube.com/results?search_query=tutorial+[MASUKKAN_TOPIK_HARI_1_DI_SINI]+bahasa+indonesia" }}] }},
          "d2": {{ "title": "Topik Hari 2", "desc": "Aktivitas belajar Hari 2", "resources": [{{ "title": "Baca Tutorial di Google", "link": "https://www.google.com/search?q=tutorial+[MASUKKAN_TOPIK_HARI_2_DI_SINI]+bahasa+indonesia" }}, {{ "title": "Tonton Video di YouTube", "link": "https://www.youtube.com/results?search_query=tutorial+[MASUKKAN_TOPIK_HARI_2_DI_SINI]+bahasa+indonesia" }}] }},
          "d3": {{ "title": "Topik Hari 3", "desc": "Aktivitas belajar Hari 3", "resources": [{{ "title": "Baca Tutorial di Google", "link": "https://www.google.com/search?q=tutorial+[MASUKKAN_TOPIK_HARI_3_DI_SINI]+bahasa+indonesia" }}, {{ "title": "Tonton Video di YouTube", "link": "https://www.youtube.com/results?search_query=tutorial+[MASUKKAN_TOPIK_HARI_3_DI_SINI]+bahasa+indonesia" }}] }},
          "d4": {{ "title": "Topik Hari 4", "desc": "Aktivitas belajar Hari 4", "resources": [{{ "title": "Baca Tutorial di Google", "link": "https://www.google.com/search?q=tutorial+[MASUKKAN_TOPIK_HARI_4_DI_SINI]+bahasa+indonesia" }}, {{ "title": "Tonton Video di YouTube", "link": "https://www.youtube.com/results?search_query=tutorial+[MASUKKAN_TOPIK_HARI_4_DI_SINI]+bahasa+indonesia" }}] }},
          "d5": {{ "title": "Topik Hari 5", "desc": "Aktivitas belajar Hari 5", "resources": [{{ "title": "Baca Tutorial di Google", "link": "https://www.google.com/search?q=tutorial+[MASUKKAN_TOPIK_HARI_5_DI_SINI]+bahasa+indonesia" }}, {{ "title": "Tonton Video di YouTube", "link": "https://www.youtube.com/results?search_query=tutorial+[MASUKKAN_TOPIK_HARI_5_DI_SINI]+bahasa+indonesia" }}] }},
          "d6": {{ "title": "Topik Hari 6", "desc": "Aktivitas belajar Hari 6", "resources": [{{ "title": "Baca Tutorial di Google", "link": "https://www.google.com/search?q=tutorial+[MASUKKAN_TOPIK_HARI_6_DI_SINI]+bahasa+indonesia" }}, {{ "title": "Tonton Video di YouTube", "link": "https://www.youtube.com/results?search_query=tutorial+[MASUKKAN_TOPIK_HARI_6_DI_SINI]+bahasa+indonesia" }}] }}
        }},
        "W2": {{
          "tag": "Fokus Topik Utama Minggu 2",
          "title": "Judul Pembelajaran Minggu 2",
          "d1": {{ "title": "Topik Hari 1", "desc": "Aktivitas belajar Hari 1", "resources": [{{ "title": "Baca Tutorial di Google", "link": "https://www.google.com/search?q=tutorial+[MASUKKAN_TOPIK_HARI_1_DI_SINI]+bahasa+indonesia" }}, {{ "title": "Tonton Video di YouTube", "link": "https://www.youtube.com/results?search_query=tutorial+[MASUKKAN_TOPIK_HARI_1_DI_SINI]+bahasa+indonesia" }}] }},
          "d2": {{ "title": "Topik Hari 2", "desc": "Aktivitas belajar Hari 2", "resources": [{{ "title": "Baca Tutorial di Google", "link": "https://www.google.com/search?q=tutorial+[MASUKKAN_TOPIK_HARI_2_DI_SINI]+bahasa+indonesia" }}, {{ "title": "Tonton Video di YouTube", "link": "https://www.youtube.com/results?search_query=tutorial+[MASUKKAN_TOPIK_HARI_2_DI_SINI]+bahasa+indonesia" }}] }},
          "d3": {{ "title": "Topik Hari 3", "desc": "Aktivitas belajar Hari 3", "resources": [{{ "title": "Baca Tutorial di Google", "link": "https://www.google.com/search?q=tutorial+[MASUKKAN_TOPIK_HARI_3_DI_SINI]+bahasa+indonesia" }}, {{ "title": "Tonton Video di YouTube", "link": "https://www.youtube.com/results?search_query=tutorial+[MASUKKAN_TOPIK_HARI_3_DI_SINI]+bahasa+indonesia" }}] }},
          "d4": {{ "title": "Topik Hari 4", "desc": "Aktivitas belajar Hari 4", "resources": [{{ "title": "Baca Tutorial di Google", "link": "https://www.google.com/search?q=tutorial+[MASUKKAN_TOPIK_HARI_4_DI_SINI]+bahasa+indonesia" }}, {{ "title": "Tonton Video di YouTube", "link": "https://www.youtube.com/results?search_query=tutorial+[MASUKKAN_TOPIK_HARI_4_DI_SINI]+bahasa+indonesia" }}] }},
          "d5": {{ "title": "Topik Hari 5", "desc": "Aktivitas belajar Hari 5", "resources": [{{ "title": "Baca Tutorial di Google", "link": "https://www.google.com/search?q=tutorial+[MASUKKAN_TOPIK_HARI_5_DI_SINI]+bahasa+indonesia" }}, {{ "title": "Tonton Video di YouTube", "link": "https://www.youtube.com/results?search_query=tutorial+[MASUKKAN_TOPIK_HARI_5_DI_SINI]+bahasa+indonesia" }}] }},
          "d6": {{ "title": "Topik Hari 6", "desc": "Aktivitas belajar Hari 6", "resources": [{{ "title": "Baca Tutorial di Google", "link": "https://www.google.com/search?q=tutorial+[MASUKKAN_TOPIK_HARI_6_DI_SINI]+bahasa+indonesia" }}, {{ "title": "Tonton Video di YouTube", "link": "https://www.youtube.com/results?search_query=tutorial+[MASUKKAN_TOPIK_HARI_6_DI_SINI]+bahasa+indonesia" }}] }}
        }},
        "W3": {{
          "tag": "Fokus Topik Utama Minggu 3",
          "title": "Judul Pembelajaran Minggu 3",
          "d1": {{ "title": "Topik Hari 1", "desc": "Aktivitas belajar Hari 1", "resources": [{{ "title": "Baca Tutorial di Google", "link": "https://www.google.com/search?q=tutorial+[MASUKKAN_TOPIK_HARI_1_DI_SINI]+bahasa+indonesia" }}, {{ "title": "Tonton Video di YouTube", "link": "https://www.youtube.com/results?search_query=tutorial+[MASUKKAN_TOPIK_HARI_1_DI_SINI]+bahasa+indonesia" }}] }},
          "d2": {{ "title": "Topik Hari 2", "desc": "Aktivitas belajar Hari 2", "resources": [{{ "title": "Baca Tutorial di Google", "link": "https://www.google.com/search?q=tutorial+[MASUKKAN_TOPIK_HARI_2_DI_SINI]+bahasa+indonesia" }}, {{ "title": "Tonton Video di YouTube", "link": "https://www.youtube.com/results?search_query=tutorial+[MASUKKAN_TOPIK_HARI_2_DI_SINI]+bahasa+indonesia" }}] }},
          "d3": {{ "title": "Topik Hari 3", "desc": "Aktivitas belajar Hari 3", "resources": [{{ "title": "Baca Tutorial di Google", "link": "https://www.google.com/search?q=tutorial+[MASUKKAN_TOPIK_HARI_3_DI_SINI]+bahasa+indonesia" }}, {{ "title": "Tonton Video di YouTube", "link": "https://www.youtube.com/results?search_query=tutorial+[MASUKKAN_TOPIK_HARI_3_DI_SINI]+bahasa+indonesia" }}] }},
          "d4": {{ "title": "Topik Hari 4", "desc": "Aktivitas belajar Hari 4", "resources": [{{ "title": "Baca Tutorial di Google", "link": "https://www.google.com/search?q=tutorial+[MASUKKAN_TOPIK_HARI_4_DI_SINI]+bahasa+indonesia" }}, {{ "title": "Tonton Video di YouTube", "link": "https://www.youtube.com/results?search_query=tutorial+[MASUKKAN_TOPIK_HARI_4_DI_SINI]+bahasa+indonesia" }}] }},
          "d5": {{ "title": "Topik Hari 5", "desc": "Aktivitas belajar Hari 5", "resources": [{{ "title": "Baca Tutorial di Google", "link": "https://www.google.com/search?q=tutorial+[MASUKKAN_TOPIK_HARI_5_DI_SINI]+bahasa+indonesia" }}, {{ "title": "Tonton Video di YouTube", "link": "https://www.youtube.com/results?search_query=tutorial+[MASUKKAN_TOPIK_HARI_5_DI_SINI]+bahasa+indonesia" }}] }},
          "d6": {{ "title": "Topik Hari 6", "desc": "Aktivitas belajar Hari 6", "resources": [{{ "title": "Baca Tutorial di Google", "link": "https://www.google.com/search?q=tutorial+[MASUKKAN_TOPIK_HARI_6_DI_SINI]+bahasa+indonesia" }}, {{ "title": "Tonton Video di YouTube", "link": "https://www.youtube.com/results?search_query=tutorial+[MASUKKAN_TOPIK_HARI_6_DI_SINI]+bahasa+indonesia" }}] }}
        }},
        "W4": {{
          "tag": "Fokus Topik Utama Minggu 4",
          "title": "Judul Pembelajaran Minggu 4",
          "d1": {{ "title": "Topik Hari 1", "desc": "Aktivitas belajar Hari 1", "resources": [{{ "title": "Baca Tutorial di Google", "link": "https://www.google.com/search?q=tutorial+[MASUKKAN_TOPIK_HARI_1_DI_SINI]+bahasa+indonesia" }}, {{ "title": "Tonton Video di YouTube", "link": "https://www.youtube.com/results?search_query=tutorial+[MASUKKAN_TOPIK_HARI_1_DI_SINI]+bahasa+indonesia" }}] }},
          "d2": {{ "title": "Topik Hari 2", "desc": "Aktivitas belajar Hari 2", "resources": [{{ "title": "Baca Tutorial di Google", "link": "https://www.google.com/search?q=tutorial+[MASUKKAN_TOPIK_HARI_2_DI_SINI]+bahasa+indonesia" }}, {{ "title": "Tonton Video di YouTube", "link": "https://www.youtube.com/results?search_query=tutorial+[MASUKKAN_TOPIK_HARI_2_DI_SINI]+bahasa+indonesia" }}] }},
          "d3": {{ "title": "Topik Hari 3", "desc": "Aktivitas belajar Hari 3", "resources": [{{ "title": "Baca Tutorial di Google", "link": "https://www.google.com/search?q=tutorial+[MASUKKAN_TOPIK_HARI_3_DI_SINI]+bahasa+indonesia" }}, {{ "title": "Tonton Video di YouTube", "link": "https://www.youtube.com/results?search_query=tutorial+[MASUKKAN_TOPIK_HARI_3_DI_SINI]+bahasa+indonesia" }}] }},
          "d4": {{ "title": "Topik Hari 4", "desc": "Aktivitas belajar Hari 4", "resources": [{{ "title": "Baca Tutorial di Google", "link": "https://www.google.com/search?q=tutorial+[MASUKKAN_TOPIK_HARI_4_DI_SINI]+bahasa+indonesia" }}, {{ "title": "Tonton Video di YouTube", "link": "https://www.youtube.com/results?search_query=tutorial+[MASUKKAN_TOPIK_HARI_4_DI_SINI]+bahasa+indonesia" }}] }},
          "d5": {{ "title": "Topik Hari 5", "desc": "Aktivitas belajar Hari 5", "resources": [{{ "title": "Baca Tutorial di Google", "link": "https://www.google.com/search?q=tutorial+[MASUKKAN_TOPIK_HARI_5_DI_SINI]+bahasa+indonesia" }}, {{ "title": "Tonton Video di YouTube", "link": "https://www.youtube.com/results?search_query=tutorial+[MASUKKAN_TOPIK_HARI_5_DI_SINI]+bahasa+indonesia" }}] }},
          "d6": {{ "title": "Topik Hari 6", "desc": "Aktivitas belajar Hari 6", "resources": [{{ "title": "Baca Tutorial di Google", "link": "https://www.google.com/search?q=tutorial+[MASUKKAN_TOPIK_HARI_6_DI_SINI]+bahasa+indonesia" }}, {{ "title": "Tonton Video di YouTube", "link": "https://www.youtube.com/results?search_query=tutorial+[MASUKKAN_TOPIK_HARI_6_DI_SINI]+bahasa+indonesia" }}] }}
        }}
      }},
      "note": "Tulis catatan edukasi/motivasi kustom di sini yang menjelaskan mengapa kurikulum ini dipotong pendek (jika gap kecil) ATAU dicicil ke dasar dulu (jika gap besar)."
    }}
    """

    # Mengaktifkan JSON Mode murni di Gemini API
    response = model.generate_content(
        prompt_template,
        generation_config={"response_mime_type": "application/json", "temperature": 0.2}
    )

    # Check if a text response is available
    if response and response.text:
        return response.text
    else:
        # Return an error JSON string if the model failed to generate content
        print(f"Warning: Gemini API did not return valid text. Full response: {response.candidates}")
        return json.dumps({"error": "Gemini model failed to generate a roadmap. Please try again or adjust your input."})

# Ambil hasil dari fungsi analyze_selected_job
# user_input = "python, hadoop" # Ini sudah didefinisikan sebelumnya
# selected_job = "Data Analyst" # Ini sudah didefinisikan sebelumnya
# result = analyze_selected_job(user_input, selected_job, data_grouped, model) # Ini juga sudah dieksekusi

# Ekstrak matched_skills dan missing_skills dari hasil
matched_skills_str = ", ".join(result['matched_skills']) if result['matched_skills'] else "Tidak ada"
missing_skills_str = ", ".join(result['missing_skills']) if result['missing_skills'] else "Tidak ada"
gap_pct = result.get('gap_percentage', '0.00%')
readiness_scr = result.get('readiness_score', '0.00%')

print("🤖 Gemini sedang menyusun kurikulum JSON adaptif (Iterative) sesuai mockup...")
print("--------------------------------------------------------------------------")

try:
    # 1. Memanggil fungsi AI dengan menyertakan skor gap dinamis
    json_output_raw = generate_roadmap_json(
        user_skills=matched_skills_str,
        job_title=result['job'],
        missing_skills=missing_skills_str,
        gap_percentage=gap_pct,
        readiness_score=readiness_scr
    )

    # 2. Mengubah string JSON dari Gemini menjadi Dictionary Python
    data_roadmap = json.loads(json_output_raw)

    # 3. Menampilkan hasil JSON secara rapi (Pretty Print)
    print("\nBERHASIL! Kurikulum berhasil dikemas dinamis berdasarkan tingkat kesulitan:")
    print(json.dumps(data_roadmap, indent=2, ensure_ascii=False))

    # 4. Menyimpan menjadi file fisik untuk diserahkan ke Orang 4 (Integrator)
    with open('roadmap_result.json', 'w', encoding='utf-8') as f:
        json.dump(data_roadmap, f, indent=2, ensure_ascii=False)
    print("\n💾 File 'roadmap_result.json' berhasil diperbarui! Siap dikonsumsi Frontend.")

except Exception as e:
    print("\n Terjadi kendala teknis saat memproses prompt Gemini.")
    print(f"Detail kendala: {e}")