import pandas as pd

df = pd.read_csv(
    "data/raw/mergeFile.csv",
    low_memory=False
)

top_titles = (
    df["jobTitle"]
    .value_counts()
    .head(200)
)

for i, title in enumerate(top_titles.index, start=1):
    print(f"{i}. {title}")