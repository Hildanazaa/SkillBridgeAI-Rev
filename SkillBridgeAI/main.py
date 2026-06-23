import json

from core_logic import get_recommendations, get_skill_gap


def main():

    print("\n===================================")
    print("        SkillBridge AI")
    print("===================================\n")

    user_skill_text = input(
        "Masukkan skill Anda (pisahkan dengan koma): "
    )

    recommendation_result = get_recommendations(
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

    if not recommendation_result["success"] or len(recommendation_result["recommendations"]) == 0:
        print("\n===================================")
        print("Process Terminated: No matching careers found.")
        print("===================================\n")
        return

    top_career = recommendation_result[
        "recommendations"
    ][0]["career"]

    skill_gap_result = get_skill_gap(
        user_skill_text=user_skill_text,
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