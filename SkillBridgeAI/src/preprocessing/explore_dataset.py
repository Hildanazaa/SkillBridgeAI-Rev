import pandas as pd
import os

RAW_FOLDER = "data/raw"

for file in os.listdir(RAW_FOLDER):

    if file.endswith(".csv"):

        path = os.path.join(
            RAW_FOLDER,
            file
        )

        try:

            df = pd.read_csv(path)

            print("\n" + "=" * 50)
            print(file)

            print("Rows :", len(df))
            print("Columns :")

            print(df.columns.tolist())

        except Exception as e:

            print(file)
            print(e)