import pandas as pd

df = pd.read_csv(
    "data/raw/mergeFile.csv",
    low_memory=False
)

job_counts = df["jobTitle"].value_counts()

print(
    "Job title > 50:",
    (job_counts > 50).sum()
)

print(
    "Job title > 100:",
    (job_counts > 100).sum()
)

print(
    "Job title > 200:",
    (job_counts > 200).sum()
)