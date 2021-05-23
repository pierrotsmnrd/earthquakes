import json
import pandas as pd
import os

from pdb import set_trace as bp

input_dir = "../data/json"

output_dir = "../data/viz/"

os.makedirs(output_dir, exist_ok=True)


# list of all the json files to build the dataset from
input_files = [(year, l)
               for year in sorted(os.listdir(input_dir)) if not year.startswith(".")
               # and int(year) > 2019
               for l in sorted(os.listdir(os.path.join(input_dir, year)))
               if l.endswith(".json")]


full_data = []

for year, file in input_files:

    print(file)
    file_path = os.path.join(input_dir, year, file)

    with open(file_path) as f:
        raw_data = f.read()
        data = json.loads(raw_data)

        print(data["metadata"]["totalCount"])

        for f in data["features"]:
            f["properties"]["id"] = f["id"]

            full_data.append(f["properties"])


output_file = os.path.join(output_dir, f"dataset.csv")
pd.DataFrame(full_data).to_csv(output_file, index=False, sep=";")

print("DONE")
