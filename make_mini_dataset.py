import json
import csv

INPUT_JSON  = "dataset/ski_resorts.json"
INPUT_CSV   = "dataset/resort_distances.csv"
OUTPUT_JSON = "dataset_mini/ski_resorts.json"
OUTPUT_CSV  = "dataset_mini/resort_distances.csv"

NUM_RESORTS = 20

SELECTED_NAMES = [
    "Vail",
    "Breckenridge",
    "Telluride",
    "Steamboat Springs",
    "Crested Butte",
    "Alta",
    "Snowbird",
    "Park City Mountain",
    "Stowe",
    "Jay Peak",
    "Killington",
    "Mammoth Mountain",
    "Kirkwood",
    "Jackson Hole",
    "Grand Targhee",
    "Big Sky",
    "Whitefish Mountain",
    "Sun Valley",
    "Wolf Creek",
    "Monarch Mountain",
]

def main():
    with open(INPUT_JSON) as f:
        all_resorts = json.load(f)["ski_resorts"]

    all_names = [r["name"] for r in all_resorts]

    # Resolve selected subset
    if SELECTED_NAMES:
        missing = [n for n in SELECTED_NAMES if n not in all_names]
        if missing:
            raise ValueError(f"Resort(s) not found in JSON: {missing}")
        selected = [r for r in all_resorts if r["name"] in SELECTED_NAMES]
    else:
        selected = all_resorts[:NUM_RESORTS]

    n = len(selected)
    if n > 31:
        raise ValueError(
            f"Too many resorts ({n}). Keep n <= 31 to stay under 1000 variables."
        )

    print(f"Selected {n} resorts")
    print(f"  Variables  : {n**2}  (limit 1000)")
    print(f"  Constraints: {1 + 3*n}  (limit 1000)")

    with open(INPUT_CSV, newline="") as f:
        reader = csv.reader(f)
        header = next(reader)
        col_names = header[1:]
        all_rows = list(reader)

    name_to_idx = {name: i for i, name in enumerate(col_names)}

    selected_names = [r["name"] for r in selected]

    with open(OUTPUT_JSON, "w") as f:
        json.dump({"ski_resorts": selected}, f, indent=2)
    print(f"Wrote {OUTPUT_JSON}")

    mini_header = [""] + selected_names

    with open(OUTPUT_CSV, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(mini_header)
        for row_name in selected_names:
            row_idx = name_to_idx[row_name]
            full_row = all_rows[row_idx]
            mini_row = [
                full_row[name_to_idx[col_name]]
                for col_name in selected_names
            ]
            writer.writerow(mini_row)

    print(f"Wrote {OUTPUT_CSV}")


if __name__ == "__main__":
    main()