import streamlit as st
from core_logic import (
    get_recommendations as _get_recommendations,
    get_match_score,
    get_roadmap as _get_roadmap
)

# ==========================================================
# GET ALL CAREERS (untuk dropdown kolom kanan)
# ==========================================================
def get_all_careers() -> list:
    try:
        from src.recommender.recommend import get_all_registered_careers
        return get_all_registered_careers()
    except Exception as e:
        print("GET ALL CAREERS ERROR:", str(e))
        return []
 
# ==========================================================
# RECOMMENDATION
# ==========================================================
def get_recommendations(user_text: str):
 
    try:
 
        raw = _get_recommendations(user_skill_text=user_text, top_k=5)
 
        if not raw.get("success"):
            return {
                "success": False,
                "recommendations": [],
                "message": raw.get("message", "Unknown error")
            }
 
        recs = []
 
        for r in raw.get("recommendations", []):
 
            score = r.get("score", 0)
 
            recs.append({
                "title": r.get("career", ""),
                "description": r.get("description", ""),
                "suitability": r.get("suitability", ""),
                "experience_level": "",
                "match_score": round(score / 100, 4),
                "matched_skills": [],
                "missing_skills": []
            })
 
        return {
            "success": True,
            "recommendations": recs,
            "message": ""
        }
 
    except Exception as e:
 
        return {
            "success": False,
            "recommendations": [],
            "message": str(e)
        }
 
 
# ==========================================================
# SKILL GAP ANALYSIS
# ==========================================================
def get_analysis(user_text: str, target_title: str):
 
    try:
 
        score_raw = get_match_score(
            user_skill_text=user_text,
            target_career=target_title
        )
 
        readiness_str = score_raw.get("readiness_score", "0.00%")
 
        try:
            readiness = int(float(readiness_str.replace("%", "")))
        except Exception:
            readiness = 0
 
        owned = score_raw.get("matched_skills", [])
 
        missing = sorted(list(set(score_raw.get("missing_skills", []))))
 
        gap_pct = score_raw.get("gap_percentage", "100.00%")
 
        return {
            "success": True,
            "readiness_score": readiness,
            "owned_skills": owned,
            "missing_skills_priority": [
                {
                    "skill": skill,
                    "priority": i + 1,
                    "reason": ""
                }
                for i, skill in enumerate(missing)
            ],
            "summary": (
                f"Kamu memiliki {len(owned)} dari "
                f"{len(owned) + len(missing)} skill "
                f"yang dibutuhkan untuk posisi {target_title}."
            ),
            "_gap_percentage": gap_pct,
            "_readiness_str": readiness_str,
            "_missing_raw": missing
        }
 
    except Exception as e:
 
        return {
            "success": False,
            "message": str(e),
            "readiness_score": 0,
            "owned_skills": [],
            "missing_skills_priority": [],
            "_gap_percentage": "100.00%",
            "_readiness_str": "0.00%",
            "_missing_raw": []
        }
 
 
# ==========================================================
# ROADMAP GENERATOR
# ==========================================================
def get_roadmap(
    target_title: str,
    missing_skills: list,
    gap_percentage="100%",
    readiness_score="0%"
):
 
    try:
 
        import json
 
        user_text = st.session_state.get("user_skills_text", "")
        analysis = st.session_state.get("analysis", {}) or {}
 
        gap_pct = analysis.get("_gap_percentage", "100.00%")
        readiness_str = analysis.get("_readiness_str", "0.00%")
 
        raw = _get_roadmap(
            user_skill_text=user_text,
            target_career=target_title,
            missing_skills=missing_skills,
            gap_percentage=gap_pct,
            readiness_score=readiness_str
        )
 
        if not raw.get("success"):
            return {"success": False, "weeks": []}
 
        data = raw.get("data", {})
 
        if isinstance(data, str):
            try:
                data = json.loads(data)
            except Exception:
                return {"success": False, "weeks": []}
 
        roadmap_data = {}
 
        if isinstance(data, dict):
            roadmap_data = data.get("roadmap", {})
 
        if not isinstance(roadmap_data, dict):
            return {"success": False, "weeks": []}
 
        weeks = []
 
        for w_key, w_data in roadmap_data.items():
 
            if not isinstance(w_data, dict):
                continue
 
            days = []
 
            for d_key, d_data in w_data.items():
 
                if d_key in ("tag", "title"):
                    continue
 
                if not isinstance(d_data, dict):
                    continue
 
                resources = d_data.get("resources", [])
                resource_link = "#"
 
                if isinstance(resources, list) and len(resources) > 0:
                    first = resources[0]
                    if isinstance(first, dict):
                        resource_link = first.get("link", "#")
 
                days.append({
                    "day": d_key.replace("d", ""),
                    "topic": d_data.get("title", ""),
                    "detail": d_data.get("desc", ""),
                    "resource": resource_link
                })
 
            weeks.append({
                "week": w_key,
                "focus": w_data.get("tag", f"Minggu {w_key}"),
                "days": days
            })
 
        return {
            "success": True,
            "weeks": weeks
        }
 
    except Exception as e:
 
        print("ROADMAP ERROR:", str(e))
 
        return {
            "success": False,
            "weeks": []
        }
 