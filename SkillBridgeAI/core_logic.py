import json

from src.recommender.recommend import recommend_career
from src.skill_extraction.skill_gap import analyze_skill_gap
from src.roadmap.generator import generate_roadmap_json


def validate_input(user_skill_text: str):
    if not user_skill_text:
        return False, "Masukkan minimal 1 skill"

    if len(user_skill_text.strip()) < 2:
        return False, "Input skill terlalu pendek"

    return True, None


def get_recommendations(
    user_skill_text: str,
    top_k: int = 5
):
    return recommend_career(
        user_skill_text=user_skill_text,
        top_k=top_k
    )


def get_skill_gap(
    user_skill_text: str,
    target_career: str
):
    user_skills = [
        skill.strip()
        for skill in user_skill_text.split(",")
        if skill.strip()
    ]

    return analyze_skill_gap(
        user_skills=user_skills,
        target_career=target_career
    )


def get_roadmap(
    user_skill_text: str,
    target_career: str,
    missing_skills: list
):
    try:
        roadmap_raw = generate_roadmap_json(
            user_skills=user_skill_text,
            job_title=target_career,
            job_requirements=", ".join(missing_skills)
        )

        try:
            roadmap_data = json.loads(roadmap_raw)

            return {
                "success": True,
                "data": roadmap_data
            }

        except Exception:
            return {
                "success": True,
                "data": roadmap_raw
            }

    except Exception as e:
        return {
            "success": False,
            "message": str(e)
        }


def analyze_user(
    user_skill_text: str,
    selected_career: str = None,
    top_k: int = 5
):
    valid, error = validate_input(user_skill_text)

    if not valid:
        return {
            "success": False,
            "message": error
        }

    recommendation_result = get_recommendations(
        user_skill_text=user_skill_text,
        top_k=top_k
    )

    if not recommendation_result["success"]:
        return recommendation_result

    recommendations = recommendation_result["recommendations"]

    if len(recommendations) == 0:
        return {
            "success": False,
            "message": "Tidak ada rekomendasi karir ditemukan"
        }

    if selected_career is None:
        selected_career = recommendations[0]["career"]

    skill_gap_result = get_skill_gap(
        user_skill_text=user_skill_text,
        target_career=selected_career
    )

    result = {
        "success": True,
        "recommendations": recommendations,
        "selected_career": selected_career,
        "skill_gap": skill_gap_result
    }

    if skill_gap_result["success"]:
        roadmap_result = get_roadmap(
            user_skill_text=user_skill_text,
            target_career=selected_career,
            missing_skills=skill_gap_result["missing_skills"]
        )

        result["roadmap"] = roadmap_result

    return result
