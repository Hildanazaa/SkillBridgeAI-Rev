import pandas as pd

df = pd.read_csv(
    "data/raw/mergeFile.csv",
    low_memory=False
)

print(
    df["categoriesName"]
    .value_counts()
    .head(50)
)