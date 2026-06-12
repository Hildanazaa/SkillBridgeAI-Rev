import pandas as pd

df = pd.read_csv(
    "data/raw/mergeFile.csv"
)

print(df.shape)

print("\nJumlah Job Title Unik:")
print(df["jobTitle"].nunique())

print("\n20 Job Title Teratas:")
print(
    df["jobTitle"]
    .value_counts()
    .head(20)
)