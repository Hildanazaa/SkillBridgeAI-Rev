import streamlit as st

def init_session_state():
    defaults = {
        "user_skills_text": "",
        "recommendations": None,
        "selected_career": None,
        "analysis": None,
        "roadmap": None,
        "show_recommendations": False,
        "show_evaluation": False,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value
