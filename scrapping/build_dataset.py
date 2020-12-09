import json
import pandas as pd
import os

from pdb import set_trace as bp

input_dir = "../data/json"

output_file = "../data/viz/earthquakes.csv"

# list of all the json files to build the dataset from
input_files = [l for l in sorted(os.listdir(input_dir)) if l.endswith(".json")]


df = None

for file in input_files:
    print(file)

    file_path = os.path.join(input_dir, file)

    with open(file_path) as f:
        raw_data = f.read()
        data = json.loads(raw_data)

        for f in data["features"]:
            f["properties"]["id"] = f["id"]

            # print(f["properties"])
            if df is None:
                df = pd.DataFrame([f["properties"]])
            else:
                df = df.append([f["properties"]])

    # save the result dataset after each json. Handy if interrupting in the middle of the process.
    df.to_csv(output_file, index=False, sep=";")


print("DONE")
