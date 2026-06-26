from src.recommender.recommend import recommend_career

result = recommend_career(
    "python, sql, excel, pandas, numpy, data visualization, power bi",
    top_k=5
)

for r in result["recommendations"]:
    print(f"{r['career']} | Score: {r['score']:.2f} | {r['suitability']}")
