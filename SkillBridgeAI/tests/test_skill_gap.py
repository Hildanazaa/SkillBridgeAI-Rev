import sys
import os

sys.path.append(
    os.path.abspath(
        os.path.join(
            os.path.dirname(__file__),
            ".."
        )
    )
)

from src.skill_extraction.skill_gap import analyze_skill_gap

result = analyze_skill_gap(
    user_skills=[
        "html",
        "css",
        "javascript"
    ],
    target_career="Frontend Developer"
)

print(result)