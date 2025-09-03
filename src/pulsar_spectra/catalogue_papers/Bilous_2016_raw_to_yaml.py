import yaml
import psrqpy
import csv

query = psrqpy.QueryATNF(params=['PSRJ', 'NAME', 'PSRB']).pandas

with open("Bilous_2016_raw.tsv", "r") as raw_file:
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
    if row[0].startswith("#") or row[0].startswith("PSR") or row[0] == '' or row[0].startswith('-'):
        continue
    print(row)

    if row[0].startswith("B"):
        bname = row[0].strip().replace("–", "-")
        pid = list(query['PSRB']).index(bname)
        pulsar = query['PSRJ'][pid]
    else:
        pulsar = row[0].strip().replace("–", "-")
    # Wrong names I found
    if pulsar == "J0435+27":
        pulsar = "J0435+2749"
    elif pulsar == "J0943+22":
        pulsar = "J0943+2253"
    elif pulsar == "J0947+27":
        pulsar = "J0947+2740"
    elif pulsar == "J1238+21":
        pulsar = "J1238+2152"
    elif pulsar == "J1246+22":
        pulsar = "J1246+2253"

    if row[1] == '<':
        continue
    flux = float(row[2])
    flux_err = float(row[3])
    pulsar_dict[pulsar] = {
        "Frequency MHz":[149],
        "Bandwidth MHz":[78],
        "Flux Density mJy":[flux],
        "Flux Density error mJy":[flux_err]
    }

with open("Bilous_2016.yaml", "w") as cat_file:
    yaml.safe_dump(pulsar_dict, cat_file, sort_keys=False, indent=2)