import pandas as pd
import numpy as np
from sentence_transformers import SentenceTransformer

print("Loading career profiles raw...")
df = pd.read_csv(
    "data/processed/career_profiles_raw.csv"
)

print("Loading model paraphrase-multilingual-MiniLM-L12-v2...")
model = SentenceTransformer(
    "paraphrase-multilingual-MiniLM-L12-v2"
)

print("Generating embeddings with averaging...")
unique_careers = df["career"].unique()
unique_embeddings = []

for i, career in enumerate(unique_careers):
    profiles = df[df["career"] == career]["profile"].tolist()
    
    # Generate embeddings for all profiles of this career
    emb = model.encode(
        profiles,
        show_progress_bar=False,
        convert_to_numpy=True
    )
    
    # Calculate the average vector (mean along axis 0)
    avg_emb = np.mean(emb, axis=0)
    unique_embeddings.append(avg_emb)
    
    if (i + 1) % 50 == 0 or (i + 1) == len(unique_careers):
        print(f"Processed {i + 1}/{len(unique_careers)} careers")

embeddings_array = np.array(unique_embeddings)

# Save embeddings
np.save(
    "data/embeddings/career_embeddings.npy",
    embeddings_array
)

# Save unique career titles so recommendation indices match 1-to-1
unique_careers_df = pd.DataFrame({"career": unique_careers})
unique_careers_df.to_csv(
    "data/processed/career_profiles.csv",
    index=False
)

print("Saved embeddings and unique careers list.")
print("Shape:", embeddings_array.shape)