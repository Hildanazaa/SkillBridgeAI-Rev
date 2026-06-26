import streamlit as st
import json
import os
import sys
import pandas as pd
# Ensure current directory is in Python path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

from core_logic import analyze_user, get_recommendations

st.title("SkillBridge AI - Streamlit Backend Test")

# 1. Input skills
user_skills = st.text_input("Masukkan Skills (pisahkan dengan koma):", value="python, sql, excel, pandas, numpy, data visualization, power bi")

if st.button("Run Recommendations"):
    if not user_skills.strip():
        st.warning("Skills input is empty!")
    else:
        st.subheader("Results from get_recommendations()")
        with st.spinner("Calling get_recommendations..."):
            results = get_recommendations(user_skills)
            st.json(results)

st.divider()

# COMPLETE USER ANALYSIS TEST
st.subheader("Complete Analysis Test")

# Ambil semua daftar profesi dari database untuk kebutuhan validasi input manual
try:
    from src.recommender.recommend import careers
    list_semua_profesi_valid = sorted(careers["career"].unique().tolist())
except Exception:
    # Jika karena suatu hal import gagal, sistem otomatis membaca langsung dari file CSV
    if os.path.exists("data/processed/career_profiles.csv"):
        df_raw = pd.read_csv("data/processed/career_profiles.csv")
        # Menggunakan kolom 'career' sesuai penamaan di recommend.py
        list_semua_profesi_valid = sorted(df_raw["career"].unique().tolist())
    else:
        list_semua_profesi_valid = []

# Sediakan radio button agar pengguna bisa memilih metode penentuan profesi
metode_pilih = st.radio(
    "Bagaimana Anda ingin menentukan profesi target?",
    ["Pilih dari Rekomendasi Karir", "Cari / Input Manual Profesi Sendiri"],
    horizontal=True
)

career_param = None
bisa_lanjut_analisis = True

# OPSI A: Mengambil opsi dari hasil rekomendasi sistem secara dinamis
if metode_pilih == "Pilih dari Rekomendasi Karir":
    if user_skills.strip():
        # Memanggil fungsi get_recommendations di balik layar untuk mengisi dropdown secara otomatis
        res_rec = get_recommendations(user_skills)
        
        # Mengekstrak list rekomendasi baik dalam bentuk dictionary ataupun list langsung
        recs = []
        if isinstance(res_rec, dict):
            recs = res_rec.get("recommendations", [])
        elif isinstance(res_rec, list):
            recs = res_rec
            
        if recs:
            recommended_jobs = [rec['career'] for rec in recs if 'career' in rec]
            selected_job = st.selectbox("Silahkan pilih profesi yang disarankan:", options=recommended_jobs)
            career_param = selected_job
        else:
            st.info("Tidak ada rekomendasi karir yang cocok dengan keahlian Anda saat ini.")
            bisa_lanjut_analisis = False
    else:
        st.info("Silahkan masukkan keahlian Anda terlebih dahulu pada Langkah 1 di atas.")
        bisa_lanjut_analisis = False

# OPSI B: Input teks manual bebas dengan validasi database eksak
else:
    manual_job_input = st.text_input("Ketik profesi spesifik yang Anda inginkan (Contoh: Data Scientist, Web Developer):", value="")
    
    if manual_job_input.strip():
        input_clean = manual_job_input.strip().lower()
        daftar_profesi_lower = [job.lower() for job in list_semua_profesi_valid]
        
        if input_clean in daftar_profesi_lower:
            # Ambil penulisan asli nama profesi (sesuai huruf kapital di dataset)
            idx = daftar_profesi_lower.index(input_clean)
            career_param = list_semua_profesi_valid[idx]
            st.success(f"Profession '{career_param}' ditemukan dalam sistem! Anda siap melakukan analisis penuh.")
        else:
            # MENAMPILKAN PESAN ERROR SESUAI PERMINTAAN ANDA
            st.error("job yang anda inginkan berada diluar informasi silahkan pilih job lain")
            bisa_lanjut_analisis = False
    else:
        bisa_lanjut_analisis = False
        
# Tombol untuk menjalankan Analisis Penuh (Kesiapan Kerja + Roadmap)
if st.button("Run Full Analysis"):
    if not user_skills.strip():
        st.warning("Skills input is empty!")
    elif not bisa_lanjut_analisis or career_param is None:
        st.error("Silahkan tentukan profesi target yang valid terlebih dahulu!")
    else:
        st.subheader(f"Results from analyze_user() for '{career_param}'")
        with st.spinner("Calling analyze_user..."):
            # Kirim parameter nama karir hasil pilihan/inputan ke fungsi backend utama
            results = analyze_user(user_skills, selected_career=career_param)
            st.json(results)
