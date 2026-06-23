import streamlit as st
import json
import os
import sys

# Ensure current directory is in Python path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

from core_logic import analyze_user, get_recommendations

st.title("SkillBridge AI - Streamlit Backend Test")

# 1. Input skills
user_skills = st.text_input("Masukkan Skills (pisahkan dengan koma):", value="python, sql, excel")

if st.button("Run Recommendations"):
    if not user_skills.strip():
        st.warning("Skills input is empty!")
    else:
        st.subheader("Results from get_recommendations()")
        with st.spinner("Calling get_recommendations..."):
            results = get_recommendations(user_skills)
            st.json(results)

st.divider()

# 2. Complete User Analysis (Recommendation + Match Score + Skill Gap + Roadmap)
st.subheader("Complete Analysis Test")
target_career = st.text_input("Target Career (Optional, leave empty for top recommendation):", value="")

if st.button("Run Full Analysis"):
    if not user_skills.strip():
        st.warning("Skills input is empty!")
    else:
        st.subheader("Results from analyze_user()")
        with st.spinner("Calling analyze_user..."):
            # If target_career is empty string, pass None to auto-select the top career
            career_param = target_career.strip() if target_career.strip() else None
            results = analyze_user(user_skills, selected_career=career_param)
            st.json(results)
