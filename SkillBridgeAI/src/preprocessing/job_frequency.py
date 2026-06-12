import pandas as pd

df = pd.read_csv(
    "data/raw/mergeFile.csv"
)

job_counts = df["jobTitle"].value_counts()

print("Total Job Title:")
print(len(job_counts))

print("\nMuncul 1 Kali:")
print((job_counts == 1).sum())

print("\nMuncul < 5 Kali:")
print((job_counts < 5).sum())

print("\nMuncul > 100 Kali:")
print((job_counts > 100).sum())