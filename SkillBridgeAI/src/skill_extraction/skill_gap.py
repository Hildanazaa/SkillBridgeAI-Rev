import json
from difflib import get_close_matches
from src.skill_extraction.skills import SKILLS

_skills_lower = [s.lower() for s in SKILLS]


def normalize_skill_name(skill_name: str) -> str:
    """
    Normalize skill name to map synonyms to a standard name and auto-correct typos.
    """
    s = skill_name.lower().strip()
    mapping = {
        "reactjs": "react",
        "react.js": "react",
        "react js": "react",
        "nextjs": "next.js",
        "next.js": "next.js",
        "next js": "next.js",
        "nodejs": "node.js",
        "node.js": "node.js",
        "node js": "node.js",
        "expressjs": "express",
        "express js": "express",
        "expess js": "express",
        "expessjs": "express",
        "nestjs": "nestjs",
        "nest.js": "nestjs",
        "nest js": "nestjs",
        "powerbi": "power bi",
        "power bi": "power bi",
        "restapi": "rest api",
        "rest api": "rest api",
        "js": "javascript",
        "ts": "typescript",
    }
    
    s_mapped = mapping.get(s, s)
    if s_mapped in _skills_lower:
        return s_mapped
        
    # Fuzzy match with high similarity threshold (e.g. 75%)
    matches = get_close_matches(s_mapped, _skills_lower, n=1, cutoff=0.75)
    if matches:
        return matches[0]
        
    return s_mapped


def analyze_skill_gap(
    user_skills: list,
    target_career: str
):
    """
    Analyze user readiness for a target career.

    Parameters
    ----------
    user_skills : list[str]
        List of skills owned by user.

    target_career : str
        Career selected by user.

    Returns
    -------
    dict
        {
            success: bool,
            career: str,
            readiness_score: float,
            matching_skills: list,
            missing_skills: list,
            statistics: dict
        }
    """
    with open(
        "data/processed/career_skills.json",
        "r",
        encoding="utf-8"
    ) as f:
        career_data = json.load(f)

    career = None

    for item in career_data:

        if item["career"].lower() == target_career.lower():
            career = item
            break

    if career is None:

        careers = [
            item["career"]
            for item in career_data
        ]

        suggestions = get_close_matches(
            target_career,
            careers,
            n=5,
            cutoff=0.3
        )

        return {
            "success": False,
            "message": "Career tidak ditemukan",
            "suggestions": suggestions
        }

    normalized_user_skills = {
        normalize_skill_name(skill)
        for skill in user_skills
    }

    career_skills = [
        skill.lower()
        for skill in career["skills"]
    ]

    matched = [
        skill
        for skill in career_skills
        if normalize_skill_name(skill) in normalized_user_skills
    ]

    missing = [
        skill
        for skill in career_skills
        if normalize_skill_name(skill) not in normalized_user_skills
    ]

    score = round(
        len(matched)
        / len(career_skills)
        * 100,
        2
    ) if career_skills else 0.0

    return {
        "success": True,
        "career": career["career"],
        "readiness_score": score,
        "matching_skills": matched,
        "missing_skills": missing,
        "note": "Tidak ada data keahlian wajib yang terdaftar untuk karir ini di database." if not career_skills else None,
        "statistics": {
            "total_required_skills": len(career_skills),
            "matched_skills": len(matched),
            "missing_skills": len(missing)
        }
    }