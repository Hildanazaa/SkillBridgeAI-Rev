import google.generativeai as genai
import streamlit as st
import json

def generate_roadmap_json(user_skills, job_title, job_requirements):
    """
    Menghasilkan analisis kesenjangan keterampilan dan roadmap pembelajaran 4 minggu
    dalam format JSON terstruktur menggunakan Gemini API.
    """
    # Koneksi API
    try:
        GOOGLE_API_KEY = st.secrets["PROJECT_CELERATES"]
        genai.configure(api_key=GOOGLE_API_KEY)
    except Exception as e:
        print(f"❌ Gagal mengambil API Key. Periksa .streamlit/secrets.toml: {e}")
        return json.dumps({"error": "API Key tidak terkonfigurasi dengan benar."})
    
    # Menggunakan model Gemini terbaru untuk pemrosesan logika backend
    model = genai.GenerativeModel('gemini-2.5-flash')

    # Prompt dengan instruksi skema JSON yang ketat untuk pemetaan data ke frontend
    prompt_template = f"""
    Kamu adalah seorang Expert IT Curriculum Developer. Tugasmu adalah menganalisis kesenjangan keterampilan (skill gap)
    dan menyusun rencana pembelajaran 4 minggu dalam format JSON untuk menutup gap tersebut.

    DATA INPUT:
    - Posisi Target: {job_title}
    - Keterampilan Pengguna Saat Ini: {user_skills}
    - Keterampilan Kunci Industri: {job_requirements}

    INSTRUKSI FORMAT OUTPUT (WAJIB):
    Keluarkan HASILNYA HANYA berupa JSON valid dengan struktur di bawah ini. Jangan berikan teks pembuka atau penutup di luar JSON.
    Gunakan Bahasa Indonesia yang profesional dan solutif.

    STRUKTUR JSON YANG DIWAJIBKAN:
    {{
      "skill_gap_analysis": [
        "Sebutkan skill gap 1 yang paling krusial",
        "Sebutkan skill gap 2",
        "Sebutkan skill gap 3"
      ],
      "roadmap": {{
        "W1": {{
          "tag": "Fokus Topik Utama Minggu 1",
          "title": "Judul Pembelajaran Minggu 1",
          "d1": {{ "title": "Topik Hari 1-2", "desc": "Penjelasan detail aktivitas belajar Hari 1-2" }},
          "d2": {{ "title": "Topik Hari 3-4", "desc": "Penjelasan detail aktivitas belajar Hari 3-4" }},
          "d3": {{ "title": "Topik Hari 5-7", "desc": "Penjelasan detail aktivitas belajar Hari 5-7" }}
        }},
        "W2": {{
          "tag": "Fokus Topik Utama Minggu 2",
          "title": "Judul Pembelajaran Minggu 2",
          "d1": {{ "title": "Topik Hari 8-10", "desc": "Penjelasan detail aktivitas belajar Hari 8-10" }},
          "d2": {{ "title": "Topik Hari 11-12", "desc": "Penjelasan detail aktivitas belajar Hari 11-12" }},
          "d3": {{ "title": "Topik Hari 13-14", "desc": "Penjelasan detail aktivitas belajar Hari 13-14" }}
        }},
        "W3": {{
          "tag": "Fokus Topik Utama Minggu 3",
          "title": "Judul Pembelajaran Minggu 3",
          "d1": {{ "title": "Topik Hari 15-17", "desc": "Penjelasan detail aktivitas belajar Hari 15-17" }},
          "d2": {{ "title": "Topik Hari 18-19", "desc": "Penjelasan detail aktivitas belajar Hari 18-19" }},
          "d3": {{ "title": "Topik Hari 20-21", "desc": "Penjelasan detail aktivitas belajar Hari 20-21" }}
        }},
        "W4": {{
          "tag": "Fokus Topik Utama Minggu 4 & Project",
          "title": "Judul Pembelajaran Minggu 4",
          "d1": {{ "title": "Topik Hari 22-24", "desc": "Penjelasan detail aktivitas belajar Hari 22-24" }},
          "d2": {{ "title": "Topik Hari 25-26", "desc": "Penjelasan detail aktivitas belajar Hari 25-26" }},
          "d3": {{ "title": "Mini Project Akhir (Hari 27-28)", "desc": "Instruksi membuat 1 proyek portofolio gabungan" }}
        }}
      }}
    }}
    """

    # Memanfaatkan JSON mode untuk memastikan struktur data konsisten
    response = model.generate_content(
        prompt_template,
        generation_config={"response_mime_type": "application/json", "temperature": 0.2}
    )

    return response.text

# --- BAGIAN SIMULASI UJI COBA BAWAHAN ---
# Kode simulasi di bawah ini dibungkus agar HANYA berjalan jika kamu mengeklik "Run" langsung pada file ini,
# tetapi TIDAK AKAN berjalan atau mengganggu ketika file ini di-import oleh teman kelompokmu nanti.
if __name__ == "__main__":
    sample_user_skills = "Python dasar, HTML, CSS, Git"
    sample_job_title = "Python Backend Developer"
    sample_job_requirements = "Python; Django or Flask Framework; RESTful API; SQL Server; PostgreSQL"

    print("🤖 Memproses data input lokal via Gemini API...")
    print("-" * 60)

    try:
        json_output_raw = generate_roadmap_json(sample_user_skills, sample_job_title, sample_job_requirements)
        data_roadmap = json.loads(json_output_raw)
        print("Proses sukses! Hasil JSON:\n")
        print(json.dumps(data_roadmap, indent=2, ensure_ascii=False))
    except Exception as e:
        print(f"❌ Terjadi kesalahan uji coba: {e}")