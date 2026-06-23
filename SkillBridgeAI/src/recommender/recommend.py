import os
import logging
import warnings
import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

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

from sentence_transformers import SentenceTransformer

import json
from src.skill_extraction.skill_gap import normalize_skill_name

# Load career profiles and precomputed embeddings
_raw_careers = pd.read_csv("data/processed/career_profiles.csv")
_raw_embeddings = np.loadtxt("data/embeddings/career_embeddings.csv", delimiter=",")

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