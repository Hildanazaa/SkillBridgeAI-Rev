import json

from src.recommender.recommend import recommend_career
from src.skill_extraction.skill_gap import analyze_skill_gap


def main():

    print("\n===================================")
    print("        SkillBridge AI")
    print("===================================\n")

    # =========================
    # INPUT USER SKILL
    # =========================
    user_skill_text = input(
        "Masukkan skill Anda (pisahkan dengan koma): "
    )

    # =========================
    # STEP 1: CAREER RECOMMENDATION
    # =========================
    recommendation_result = recommend_career(
        user_skill_text
    )

    print("\n=== Top Career Recommendation ===\n")

    print(
        json.dumps(
            recommendation_result,
            indent=4,
            ensure_ascii=False
        )
    )

    # ambil top 1 career otomatis
    top_career = recommendation_result[
        "recommendations"
    ][0]["career"]

    # =========================
    # STEP 2: SKILL GAP ANALYSIS
    # =========================
    user_skills = [
        skill.strip().lower()
        for skill in user_skill_text.split(",")
    ]

    skill_gap_result = analyze_skill_gap(
        user_skills=user_skills,
        target_career=top_career
    )

    print("\n=== Skill Gap Analysis ===\n")

    print(
        json.dumps(
            skill_gap_result,
            indent=4,
            ensure_ascii=False
        )
    )

    print("\n===================================")
    print("Process Completed Successfully")
    print("===================================\n")


if __name__ == "__main__":
    main()