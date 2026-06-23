import google.generativeai as genai
import streamlit as st
import json

def generate_roadmap_json(user_skills, job_title, job_requirements, missing_skills, gap_percentage, readiness_score):
    """
    Menghasilkan analisis kesenjangan keterampilan dan roadmap pembelajaran 4 minggu
    dalam format JSON terstruktur menggunakan Gemini API.
    """
    # Koneksi API
    import os
    GOOGLE_API_KEY = os.getenv("PROJECT_CELERATES") or os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    
    if not GOOGLE_API_KEY:
        # Fallback 1: Streamlit secrets
        try:
            GOOGLE_API_KEY = st.secrets["PROJECT_CELERATES"]
        except Exception:
            pass
            
    if not GOOGLE_API_KEY:
        # Fallback 2: Manual secrets.toml parsing
        try:
            secrets_path = os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 
                ".streamlit", 
                "secrets.toml"
            )
            if os.path.exists(secrets_path):
                with open(secrets_path, "r", encoding="utf-8") as f:
                    for line in f:
                        if "PROJECT_CELERATES" in line:
                            # Extract value between quotes
                            parts = line.split("=")
                            if len(parts) > 1:
                                GOOGLE_API_KEY = parts[1].replace('"', '').replace("'", "").strip()
                                break
        except Exception:
            pass

    if not GOOGLE_API_KEY:
        print("Gagal mengambil API Key. Periksa .env, Environment Variables, atau .streamlit/secrets.toml.")
        return json.dumps({"error": "API Key tidak terkonfigurasi dengan benar."})

    try:
        genai.configure(api_key=GOOGLE_API_KEY)
    except Exception as e:
        return json.dumps({"error": f"Gagal mengonfigurasi Gemini API: {str(e)}"})
    
    # Menggunakan model Gemini terbaru untuk pemrosesan logika backend
    model = genai.GenerativeModel('gemini-2.5-flash')

    # Prompt dengan instruksi skema JSON yang ketat untuk pemetaan data ke frontend
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

    return response.text 