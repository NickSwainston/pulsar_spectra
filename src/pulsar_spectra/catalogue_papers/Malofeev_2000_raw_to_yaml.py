import csv
import yaml

import psrqpy

query = psrqpy.QueryATNF(params=["PSRJ", "NAME", "PSRB"]).pandas
all_jnames = list(query["PSRJ"])

with open("Malofeev_2000_raw.tsv", "r") as raw_file:
    tsv_file = csv.reader(raw_file, delimiter="\t")
    lines = []
    for line in tsv_file:
        lines.append(line)
    print(lines)

pulsar_dict = {}
for row in lines:
    row = [r.strip() for r in row]
    if len(row) == 0:
        continue
    if row[0].startswith("#") or row[0].startswith("PSR") or row[0] == "" or row[0].startswith("-"):
        continue
    if row[1] == "IP" or row[2] == "<" or row[2] == ">" or row[4] == "":
        continue
    print(row)

    if row[0].startswith("J"):
        pulsar = row[0].strip().replace("–", "-")
    else:
        bname = "B" + row[0].strip().replace("–", "-")
        pid = list(query["PSRB"]).index(bname)
        pulsar = query["PSRJ"][pid]
    if len(pulsar) < 10:
        # look for real name
        possible_names = []
        for jname in all_jnames:
            if jname.startswith(pulsar):
                possible_names.append(jname)
        if len(possible_names) == 1:
            pulsar = possible_names[0]
        else:
            exit()
    # Wrong names I found
    if pulsar == "J1025-0709":
        pulsar = "J1024-0719"
    elif pulsar == "J1549+2110":
        pulsar = "J1549+2113"
    elif pulsar == "J2347-0612":
        pulsar = "J2346-0609"
    elif pulsar == "J1235-5516":
        pulsar = "J1235-54"

    flux = float(row[3])
    flux_err = float(row[4])
    pulsar_dict[pulsar] = {
        "Frequency MHz": [102.5],
        "Bandwidth MHz": [0.64],
        "Flux Density mJy": [flux],
        "Flux Density error mJy": [flux_err],
    }


with open("Malofeev_2000.yaml", "w") as cat_file:
    yaml.safe_dump(pulsar_dict, cat_file, sort_keys=False, indent=2)
