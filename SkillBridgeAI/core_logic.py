# try:
#     from src.recommender.recommend import recommend_career
# except ImportError:
#     recommend_career = None

# try:
#     from src.skill_extraction.skill_gap import analyze_skill_gap
# except ImportError:
#     analyze_skill_gap = None

# try:
#     from src.scoring.scoring import calculate_target_similarity
# except ImportError:
#     calculate_target_similarity = None

# try:
#     from src.llm.explainer import explain_missing_skills
# except ImportError:
#     explain_missing_skills = None

# try:
#     from src.llm.roadmap import generate_roadmap
# except ImportError:
#     generate_roadmap = None


# def validate_input(user_skill_text):

#     if not user_skill_text:
#         return False, "Skill tidak boleh kosong"

#     if len(user_skill_text.strip()) < 2:
#         return False, "Masukkan skill yang valid"

#     return True, None


# def get_recommendations(user_skill_text, top_k=5):

#     if recommend_career is None:
#         return {
#             "success": False,
#             "message": "Recommendation module not found"
#         }

#     return recommend_career(
#         user_skill_text=user_skill_text,
#         top_k=top_k
#     )


# def get_target_career_score(
#     user_skill_text,
#     target_career
# ):

#     if calculate_target_similarity is None:

#         return {
#             "score": None,
#             "status": "waiting_for_scoring_module"
#         }

#     return calculate_target_similarity(
#         user_skill_text,
#         target_career
#     )


# def get_skill_gap(
#     user_skill_text,
#     target_career
# ):

#     if analyze_skill_gap is None:

#         return {
#             "readiness_score": 0,
#             "matching_skills": [],
#             "missing_skills": []
#         }

#     user_skills = [
#         skill.strip()
#         for skill in user_skill_text.split(",")
#         if skill.strip()
#     ]

#     return analyze_skill_gap(
#         user_skills,
#         target_career
#     )


# def get_missing_skill_explanation(
#     target_career,
#     missing_skills
# ):

#     if explain_missing_skills is None:

#         return {
#             "status": "waiting_for_gemini_module",
#             "content": None
#         }

#     return explain_missing_skills(
#         target_career,
#         missing_skills
#     )


# def get_roadmap(
#     target_career,
#     missing_skills
# ):

#     if generate_roadmap is None:

#         return {
#             "status": "waiting_for_roadmap_module",
#             "week_1": None,
#             "week_2": None,
#             "week_3": None,
#             "week_4": None
#         }

#     return generate_roadmap(
#         target_career,
#         missing_skills
#     )


# def recommendation_pipeline(
#     user_skill_text,
#     top_k=5
# ):

#     recommendations = get_recommendations(
#         user_skill_text,
#         top_k
#     )

#     if not recommendations.get("success", False):
#         return recommendations

#     return {
#         "success": True,
#         "recommendations": recommendations
#     }


# def career_analysis_pipeline(
#     user_skill_text,
#     target_career
# ):

#     score = get_target_career_score(
#         user_skill_text,
#         target_career
#     )

#     skill_gap = get_skill_gap(
#         user_skill_text,
#         target_career
#     )

#     missing_skills = skill_gap.get(
#         "missing_skills",
#         []
#     )

#     explanation = get_missing_skill_explanation(
#         target_career,
#         missing_skills
#     )

#     roadmap = get_roadmap(
#         target_career,
#         missing_skills
#     )

#     return {
#         "success": True,
#         "selected_career": target_career,
#         "match_score": score,
#         "skill_gap": skill_gap,
#         "missing_skills": missing_skills,
#         "missing_skill_explanation": explanation,
#         "roadmap": roadmap
#     }


# def process_user(
#     user_skill_text,
#     target_career=None,
#     top_k=5
# ):

#     valid, error = validate_input(
#         user_skill_text
#     )

#     if not valid:

#         return {
#             "success": False,
#             "message": error
#         }

#     recommendations = get_recommendations(
#         user_skill_text,
#         top_k
#     )

#     if not recommendations.get("success", False):
#         return recommendations

#     selected_career = target_career

#     if selected_career is None:

#         try:

#             selected_career = (
#                 recommendations["recommendations"][0]["career"]
#             )

#         except Exception:

#             selected_career = None

#     score = get_target_career_score(
#         user_skill_text,
#         selected_career
#     )

#     skill_gap = get_skill_gap(
#         user_skill_text,
#         selected_career
#     )

#     missing_skills = skill_gap.get(
#         "missing_skills",
#         []
#     )

#     explanation = get_missing_skill_explanation(
#         selected_career,
#         missing_skills
#     )

#     roadmap = get_roadmap(
#         selected_career,
#         missing_skills
#     )

#     return {
#         "success": True,
#         "recommended_careers": recommendations["recommendations"],
#         "selected_career": selected_career,
#         "match_score": score,
#         "skill_gap": skill_gap,
#         "missing_skills": missing_skills,
#         "missing_skill_explanation": explanation,
#         "roadmap": roadmap
#     }


# if __name__ == "__main__":

#     result = process_user(
#         "python, sql, pandas, machine learning"
#     )

#     from pprint import pprint

#     pprint(result)
