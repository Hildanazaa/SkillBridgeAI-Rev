import streamlit as st
from dotenv import load_dotenv
from utils.state import init_session_state
from utils.styles import inject_styles
from utils.api import get_recommendations, get_analysis, get_roadmap

load_dotenv()

# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="SkillBridge AI",
    page_icon="SkillBridgeAI.png",
    layout="wide"
)

inject_styles()
init_session_state()

# ── Header ───────────────────────────────────────────────────────
with st.container(border=True):

    col_logo, col_title = st.columns([1, 11])

    with col_logo:
        st.image("SkillBridgeAI.png", width=75)

    with col_title:
        st.markdown("""
        <h1 style="
            margin-top:0px;
            margin-bottom:0;
            font-size:42px;
            font-weight:900;
            color:#111827;
            letter-spacing:-1px;
        ">
           | SkillBridge
            <span style="
                background:#7c3aed;
                color:white;
                padding:2px 12px;
                border-radius:999px;
                font-size:16px;
                font-weight:700;
                vertical-align:middle;
            ">
                AI
            </span>
        </h1>
        """, unsafe_allow_html=True)

st.markdown(
    "<h2 style='margin:0 0 4px 0; color:#111827;'>Halo, Talenta Masa Depan! 👋</h2>",
    unsafe_allow_html=True
)

st.markdown(
    "<p style='color:#6b7280; margin-bottom:24px;'>Petakan keahlianmu, dapatkan rekomendasi karir, dan modul belajar yang dipersonalisasi.</p>",
    unsafe_allow_html=True
)

# ── Layout ───────────────────────────────────────────────────────────────────
col_left, col_right = st.columns([5, 7], gap="large")

# ═══════════════════════════════════════════════════════════
# KOLOM KIRI — Input Skill + Rekomendasi Karir
# ═══════════════════════════════════════════════════════════
with col_left:

    st.markdown("""
    <div style="background:#ffffff; border:1px solid #e5e7eb; border-radius:12px; padding:16px 20px 8px 20px; margin-bottom:8px;">
        <div style="display:flex; align-items:center; gap:8px; margin-bottom:4px;">
            <span style="font-size:16px;">📋</span>
            <span style="font-size:16px; font-weight:700; color:#111827;">Masukkan Keahlian Anda</span>
        </div>
        <p style="color:#6b7280; font-size:13px; margin:0;">Tuliskan semua skill, bahasa pemrograman, framework, atau tool yang Anda kuasai saat ini secara bebas.</p>
    </div>
    """, unsafe_allow_html=True)

    user_input = st.text_area(
        label="skill_input",
        placeholder="Saya memahami pemrograman Python dasar, analisis data sederhana dengan Microsoft Excel, dan visualisasi data menggunakan library Matplotlib.",
        height=150,
        key="input_box",
        label_visibility="collapsed"
    )

    st.markdown("""
    <style>
    .stTextArea [data-baseweb="textarea"] + div { display: none !important; }
    small, .stTextArea small { display: none !important; }
    [data-testid="InputInstructions"] { display: none !important; }
    </style>
    """, unsafe_allow_html=True)

    # ── TOMBOL ANALISIS ──────────────────────────────────────────────────────
    if st.button("Analisis Karir & Cari Rekomendasi"):
        if not user_input.strip():
            st.warning("Harap masukkan skill kamu terlebih dahulu.")
        else:
            with st.spinner("Menganalisis skill..."):
                raw = get_recommendations(user_input)
                if not raw.get("success"):
                    st.error(f"Gagal mengambil rekomendasi: {raw.get('message', 'Unknown error')}")
                else:
                    st.session_state.recommendations      = raw.get("recommendations", [])
                    st.session_state.user_skills_text     = user_input
                    st.session_state.show_recommendations = True
                    st.session_state.show_evaluation      = False
                    st.session_state.analysis             = None
                    st.session_state.roadmap              = None

    # ── HASIL REKOMENDASI ────────────────────────────────────────────────────
    if st.session_state.show_recommendations and st.session_state.recommendations:
        symbols = ["&#9644;", "&#9643;", "&#9642;", "&#9641;"]

        st.markdown("""
        <div style="background:#ffffff; border:1px solid #e5e7eb; border-radius:12px; padding:20px; margin-top:12px;">
            <div style="display:flex; align-items:center; gap:8px; margin-bottom:4px;">
                <span style="font-size:15px;">✦</span>
                <span style="font-size:15px; font-weight:700; color:#111827;">Rekomendasi Karir Terdekat</span>
            </div>
            <p style="color:#6b7280; font-size:12px; margin:0 0 14px 0;">Berdasarkan analisis kemiripan skill, berikut karir yang paling cocok dengan profil kamu:</p>
        """, unsafe_allow_html=True)

        for i, rec in enumerate(st.session_state.recommendations):
            score       = rec["match_score"] * 100 if rec["match_score"] <= 1 else rec["match_score"]
            score_color = "#16a34a" if score >= 66 else "#ca8a04" if score >= 32 else "#dc2626"
            sym         = symbols[i % len(symbols)]
            title       = rec["title"]
            level       = rec["experience_level"]

            st.markdown(
                '<div style="background:#f8fafc; border:1px solid #e5e7eb; border-radius:10px; padding:12px 14px; margin-bottom:4px; display:flex; align-items:center; justify-content:space-between;">'
                '<div style="display:flex; align-items:center; gap:12px;">'
                '<div style="width:36px; height:36px; border-radius:8px; background:#f1f5f9; border:1px solid #e2e8f0; display:flex; align-items:center; justify-content:center; font-size:15px; color:#475569; flex-shrink:0;">' + sym + '</div>'
                '<div>'
                '<div style="font-size:14px; font-weight:700; color:#111827;">' + title + '</div>'
                '<div style="font-size:11px; color:#9ca3af; margin-top:1px;">' + level + '</div>'
                '</div></div>'
                '<div style="text-align:right;">'
                '<div style="font-size:15px; font-weight:700; color:' + score_color + ';">' + f"{score:.1f}%" + '</div>'
                '<div style="font-size:10px; color:#9ca3af;">Kecocokan</div>'
                '</div></div>',
                unsafe_allow_html=True
            )

            if st.button(f"Pilih  {title}", key=f"rec_{title}"):
                st.session_state.selected_career = title
                with st.spinner("Mengevaluasi kesiapan..."):
                    analysis = get_analysis(st.session_state.user_skills_text, title)
                    missing_list = [m["skill"] for m in analysis.get("missing_skills_priority", [])]
                    roadmap = get_roadmap(title, missing_list)
                    st.session_state.analysis = analysis
                    st.session_state.roadmap = roadmap
                    st.session_state.show_evaluation = True
                st.rerun()

        st.markdown('</div>', unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════
# KOLOM KANAN — Profesi Target + Skill Gap + Roadmap
# ═══════════════════════════════════════════════════════════
with col_right:

    st.markdown("""
    <div style="background:#ffffff; border:1px solid #e5e7eb; border-radius:12px; padding:16px 20px 12px 20px; margin-bottom:8px;">
        <div style="display:flex; align-items:center; gap:8px; margin-bottom:4px;">
            <span style="font-size:16px;">◎</span>
            <span style="font-size:16px; font-weight:700; color:#111827;">Tentukan Profesi Pilihan Anda</span>
        </div>
        <p style="color:#6b7280; font-size:13px; margin:0;">Anda bebas menentukan profesi apa pun yang Anda inginkan (tidak harus sesuai dengan rekomendasi).</p>
    </div>
    """, unsafe_allow_html=True)

    recs = st.session_state.recommendations or []

    if recs:
        title_options  = ["-- Pilih Profesi Impian Anda --"] + [f"{r['title']} (Rekomendasi #{i+1})" for i, r in enumerate(recs)]
        selected_label = st.selectbox("Pilih Profesi", options=title_options, key="career_dropdown", label_visibility="collapsed")
        selected       = recs[title_options.index(selected_label) - 1]["title"] if selected_label != "-- Pilih Profesi Impian Anda --" else None
    else:
        st.selectbox("Pilih Profesi", options=["-- Pilih Profesi Impian Anda --"], key="career_dropdown", label_visibility="collapsed")
        selected = None

    # ── TOMBOL EVALUASI ──────────────────────────────────────────────────────
    if st.button("Evaluasi Kesiapan"):
        if not recs:
            st.warning("Jalankan analisis skill dulu di kolom kiri.")
        elif not selected:
            st.warning("Pilih profesi terlebih dahulu.")
        else:
            with st.spinner("Mengevaluasi..."):
                analysis = get_analysis(st.session_state.user_skills_text, selected)
                missing_list = [m["skill"] for m in analysis.get("missing_skills_priority", [])]
                roadmap = get_roadmap(selected, missing_list)
                st.session_state.selected_career = selected
                st.session_state.analysis = analysis
                st.session_state.roadmap = roadmap
                st.session_state.show_evaluation = True
            st.rerun()

    # ── HASIL EVALUASI SKILL GAP ─────────────────────────────────────────────
    if st.session_state.show_evaluation and st.session_state.analysis:
        analysis = st.session_state.analysis
        roadmap  = st.session_state.roadmap
        score    = analysis["readiness_score"]
        target   = st.session_state.selected_career

        if score >= 66:
            ring_color = "#16a34a"; kategori = "Siap Kerja (Butuh Poles Sedikit)"
            badge_bg = "#f0fdf4"; badge_color = "#15803d"; badge_border = "#bbf7d0"
        elif score >= 32:
            ring_color = "#ca8a04"; kategori = "Butuh Sedikit Upskilling"
            badge_bg = "#fefce8"; badge_color = "#92400e"; badge_border = "#fde68a"
        else:
            ring_color = "#dc2626"; kategori = "Butuh Upskilling Intensif"
            badge_bg = "#fff1f2"; badge_color = "#be123c"; badge_border = "#fecdd3"

        owned   = analysis.get("owned_skills", [])
        missing = [m["skill"] for m in analysis.get("missing_skills_priority", [])]
        n_owned = len(owned)
        n_miss  = len(missing)

        # Score card
        st.markdown(
            '<div style="background:#ffffff; border:1px solid #e5e7eb; border-radius:12px; padding:20px; margin-bottom:12px;">'
            '<p style="font-size:11px; font-weight:600; color:#9ca3af; text-transform:uppercase; letter-spacing:0.05em; margin:0 0 2px 0;">Target Karir</p>'
            '<p style="font-size:17px; font-weight:800; color:#111827; margin:0 0 16px 0;">Target: <span style="color:#1e3a5f;">' + target + '</span></p>'
            '<div style="display:flex; align-items:center; gap:20px; margin-bottom:16px;">'
            '<div style="width:90px; height:90px; border-radius:50%; border:5px solid ' + ring_color + '; display:flex; align-items:center; justify-content:center; flex-direction:column; flex-shrink:0; background:#f8fafc;">'
            '<span style="font-size:22px; font-weight:800; color:' + ring_color + '; line-height:1;">' + str(score) + '%</span>'
            '<span style="font-size:9px; text-transform:uppercase; letter-spacing:0.05em; color:#9ca3af;">SKOR KERJA</span>'
            '</div>'
            '<div style="flex:1;">'
            '<p style="margin:0 0 8px 0; font-size:13px; color:#6b7280;">Skill Anda sangat mendekati kebutuhan pasar industri!</p>'
            '<span style="font-size:12px; font-weight:600; background:' + badge_bg + '; color:' + badge_color + '; border:1px solid ' + badge_border + '; padding:4px 12px; border-radius:99px;">Kategori: ' + kategori + '</span>'
            '</div></div>'
            '<div style="display:flex; gap:12px;">'
            '<div style="flex:1; background:#f8fafc; border:1px solid #e5e7eb; border-radius:10px; padding:12px 16px; text-align:center;">'
            '<div style="font-size:22px; font-weight:800; color:#111827;">' + str(n_owned) + ' / ' + str(n_owned + n_miss) + '</div>'
            '<div style="font-size:11px; color:#6b7280; margin-top:2px;">DIMILIKI</div>'
            '</div>'
            '<div style="flex:1; background:#f8fafc; border:1px solid #e5e7eb; border-radius:10px; padding:12px 16px; text-align:center;">'
            '<div style="font-size:22px; font-weight:800; color:#111827;">' + str(n_miss) + ' Skill</div>'
            '<div style="font-size:11px; color:#6b7280; margin-top:2px;">KURANG (GAP)</div>'
            '</div></div>'
            '</div>',
            unsafe_allow_html=True
        )

        # Missing skills badges
        miss_label = '<p style="font-size:12px; font-weight:700; color:#6b7280; text-transform:uppercase; letter-spacing:0.05em; margin:0 0 8px 0;">Skill yang Kurang (Missing Skills):</p>'
        badges = "".join(['<span class="badge-missing">&#9398; ' + s + '</span>' for s in missing])
        st.markdown(
            '<div style="background:#ffffff; border:1px solid #e5e7eb; border-radius:12px; padding:16px; margin-bottom:12px;">'
            + miss_label + '<div>' + badges + '</div></div>',
            unsafe_allow_html=True
        )
        
        # Roadmap
        if roadmap:
            st.markdown("""
            <div style="background:#ffffff; border:1px solid #e5e7eb; border-radius:12px; padding:20px 20px 8px 20px; margin-bottom:4px;">
                <div style="display:flex; align-items:center; justify-content:space-between; margin-bottom:4px;">
                    <div style="display:flex; align-items:center; gap:8px;">
                        <span style="font-size:16px;">◫</span>
                        <span style="font-size:15px; font-weight:700; color:#111827;">Roadmap Belajar Terpersonalisasi (4 Minggu)</span>
                    </div>
                </div>
                <p style="color:#6b7280; font-size:12px; margin:0 0 14px 0;">Dihasilkan oleh AI berbasis deteksi gap secara zero-shot</p>
            </div>
            """, unsafe_allow_html=True)

        # =========================
        # ROADMAP
        # =========================

        if roadmap and roadmap.get("success", False):

            weeks = roadmap.get("weeks", [])

            if weeks:

                st.markdown("""
                <div style="background:#ffffff; border:1px solid #e5e7eb;
                border-radius:12px; padding:20px 20px 8px 20px; margin-bottom:4px;">
                    <div style="display:flex; align-items:center; gap:8px;">
                        <span style="font-size:16px;">◫</span>
                        <span style="font-size:15px; font-weight:700; color:#111827;">
                            Roadmap Belajar Terpersonalisasi (4 Minggu)
                        </span>
                    </div>
                    <p style="color:#6b7280; font-size:12px; margin-top:6px;">
                        Dihasilkan oleh AI berbasis deteksi gap secara zero-shot
                    </p>
                </div>
                """, unsafe_allow_html=True)

                tab_labels = [f"Minggu {w['week']}" for w in weeks]
                tabs = st.tabs(tab_labels)

                for idx, tab in enumerate(tabs):

                    with tab:

                        week = weeks[idx]

                        st.markdown(
                            f"""
                            <p style="
                            font-size:12px;
                            font-weight:700;
                            color:#6b7280;
                            text-transform:uppercase;
                            margin-bottom:12px;">
                            {week.get("focus","")}
                            </p>
                            """,
                            unsafe_allow_html=True
                        )

                        days = week.get("days", [])

                        for d in range(0, len(days), 2):

                            cols = st.columns(2)

                            for j, col in enumerate(cols):

                                if d + j < len(days):

                                    day = days[d + j]

                                    with col:

                                        st.markdown(
                                            f"""
                                            <div style="
                                            background:#1e3a5f;
                                            border-radius:10px;
                                            padding:14px 16px;
                                            margin-bottom:10px;
                                            min-height:120px;">

                                            <p style="
                                            color:white;
                                            font-weight:600;">
                                            Hari {day.get('day')} — {day.get('topic')}
                                            </p>

                                            <p style="color:#cbd5e1;">
{day.get('detail')}
</p>

<a href="{day.get('resource', '#')}"
   target="_blank"
   style="
   color:white;
   font-size:12px;
   text-decoration:none;
   font-weight:600;">
   📚 Buka Sumber Belajar
</a>

                                            </div>
                                            """,
                                            unsafe_allow_html=True
                                        )

        elif st.session_state.show_evaluation:

            st.warning(
                "⏳ Roadmap sedang diproses oleh AI atau belum tersedia. "
                "Coba klik Evaluasi Kesiapan kembali."
            )
