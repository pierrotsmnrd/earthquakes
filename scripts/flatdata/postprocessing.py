import sys
import pandas as pd
import json

#from pdb import set_trace as bp

if __name__ == "__main__":

    input_file = sys.argv[1]

    # TODO : change this to 2030 on December 31st, 2029 :)
    decade = "2020"
    output_file = f'./data/viz/{decade}.csv'

    # Build a dataframe from the latest data
    new_data = []
    with open(input_file) as f:
        raw_data = f.read()
        data = json.loads(raw_data)
        for f in data["features"]:
            f["properties"]["id"] = f["id"]
            new_data.append(f["properties"])

    new_df = pd.DataFrame(new_data)
    print(
        f"latest json holds {len(new_df)} rows. some of them may have been added already")

    # concat the existing dataframe and the new one, and drop duplicates
    df = pd.read_csv(output_file, sep=';')
    previous_row_count = len(df)

    df = pd.concat([df, new_df]).drop_duplicates(
        subset='id', keep='last').reset_index(drop=True)

    # Save
    df.to_csv(output_file, index=False, sep=";")

    new_row_count = len(df)
    print("DONE.")
    print(
        f"df has now {new_row_count} rows (+{new_row_count-previous_row_count})")
