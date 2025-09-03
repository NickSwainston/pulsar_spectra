import csv
import yaml

import psrqpy

query = psrqpy.QueryATNF(params=["PSRJ", "NAME", "PSRB", "P0"]).pandas
all_jnames = list(query["PSRJ"])

# was converted from image to csv using ABBYY FineReader
with open("Kramer_1998_raw.csv") as file:
    tsv_file = csv.reader(file, delimiter=" ")
    lines = []
    for line in tsv_file:
        lines.append(line)

pulsar_dict = {}
for row in lines:
    row = [r.strip() for r in row]

    pulsar = row[0].strip().replace("–", "-").replace(" ", "").replace("−", "-")
    if pulsar.startswith("B"):
        pid = list(query["PSRB"]).index(pulsar)
        pulsar = query["PSRJ"][pid]

    # Wrong names
    if pulsar == "J1730-2324":
        pulsar = "J1730-2304"
    if pulsar not in all_jnames:
        print(pulsar)

    freq = float(row[3]) * 1e3
    flux = float(row[4][:-1])
    flux_err = float(row[5])

    pulsar_dict[pulsar] = {
        "Frequency MHz": [freq],
        "Bandwidth MHz": [40.0],
        "Flux Density mJy": [flux],
        "Flux Density error mJy": [flux_err],
    }

with open("Kramer_1998.yaml", "w") as cat_file:
    yaml.safe_dump(pulsar_dict, cat_file, sort_keys=False, indent=2)
