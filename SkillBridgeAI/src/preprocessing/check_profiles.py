import pandas as pd

df = pd.read_csv(
    "data/processed/career_profiles.csv"
)

print(df.shape)

print(df.head())