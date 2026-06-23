import json
import logging
from datetime import datetime

from src.recommender.recommend import recommend_career
from src.skill_extraction.skill_gap import analyze_skill_gap
from src.roadmap.generator import generate_roadmap_json

try:
    from src.scoring.scoring import (
        analyze_selected_job,
        data_grouped,
        model
    )
except ImportError:
    analyze_selected_job = None
    data_grouped = None
    model = None


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)


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

    try:

        return recommend_career(
            user_skill_text=user_skill_text,
            top_k=top_k
        )

    except Exception as e:

        logging.exception("Recommendation Error")

        return {
            "success": False,
            "message": str(e)
        }


def get_match_score(
    user_skill_text: str,
    target_career: str
):

    if (
        analyze_selected_job is None
        or data_grouped is None
        or model is None
    ):

        return {
            "success": False,
            "message": "Modul scoring belum tersedia",
            "job": target_career,
            "semantic_match": None,
            "matched_skills": [],
            "missing_skills": []
        }

    try:

        result = analyze_selected_job(
            user_input_text=user_skill_text,
            selected_job_title=target_career,
            data_df=data_grouped,
            model_encoder=model
        )

        if "error" in result:

            return {
                "success": False,
                "message": result["error"],
                "job": target_career,
                "semantic_match": None,
                "matched_skills": [],
                "missing_skills": []
            }

        result["success"] = True

        return result

    except Exception as e:

        logging.exception("Scoring Error")

        return {
            "success": False,
            "message": str(e),
            "job": target_career,
            "semantic_match": None,
            "matched_skills": [],
            "missing_skills": []
        }


def get_skill_gap(
    user_skill_text: str,
    target_career: str
):

    try:

        user_skills = [
            skill.strip()
            for skill in user_skill_text.split(",")
            if skill.strip()
        ]

        return analyze_skill_gap(
            user_skills=user_skills,
            target_career=target_career
        )

    except Exception as e:

        logging.exception("Skill Gap Error")

        return {
            "success": False,
            "message": str(e)
        }


def get_roadmap(
    user_skill_text: str,
    target_career: str,
    missing_skills: list,
    gap_percentage: str = "100.00%",    
    readiness_score: str = "0.00%"
):

    try:

        roadmap_raw = generate_roadmap_json(
            user_skills=user_skill_text,
            job_title=target_career,
            job_requirements=", ".join(missing_skills),
            missing_skills=", ".join(missing_skills),
            gap_percentage=gap_percentage, # Kirim ke AI
            readiness_score=readiness_score
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

        logging.exception("Roadmap Error")

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

    if not recommendation_result.get("success"):

        return recommendation_result

    recommendations = recommendation_result.get(
        "recommendations",
        []
    )

    if not recommendations:

        return {
            "success": False,
            "message": "Tidak ada rekomendasi karir ditemukan"
        }

    if selected_career is None:

        selected_career = recommendations[0]["career"]

    score_result = get_match_score(user_skill_text, selected_career)
    
    skill_gap_result = get_skill_gap(
        user_skill_text=user_skill_text,
        target_career=selected_career
    )

    missing_skills = score_result.get(
        "missing_skills",
        []
    )

    if not missing_skills:

        missing_skills = skill_gap_result.get(
            "missing_skills",
            []
        )
    
    # 2. Ambil data untuk dikirim ke Gemini
    # Kita ambil langsung dari key yang disediakan scoring.py
    gap_pct = score_result.get("gap_percentage", "100.00%")
    readiness_scr = score_result.get("readiness_score", "0.00%")

    roadmap_result = None
    if missing_skills:
        roadmap_result = get_roadmap(
            user_skill_text=user_skill_text,
            target_career=selected_career,
            missing_skills=missing_skills,
            gap_percentage=gap_pct, 
            readiness_score=readiness_scr
        )

    return {
        "success": True,
        "timestamp": datetime.now().isoformat(),
        "selected_career": selected_career,
        "recommendations": recommendations,
        "match_score": score_result,
        "skill_gap": skill_gap_result,
        "roadmap": roadmap_result
    }


if __name__ == "__main__":

    result = analyze_user(
        user_skill_text="python, sql, excel"
    )

    print(
        json.dumps(
            result,
            indent=4,
            ensure_ascii=False
        )
    )
