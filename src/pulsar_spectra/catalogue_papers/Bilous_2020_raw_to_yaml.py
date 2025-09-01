import yaml
import psrqpy
import csv

query = psrqpy.QueryATNF(params=['PSRJ', 'NAME', 'PSRB']).pandas

with open("Bilous_2020_raw.tsv", "r") as raw_file:
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
    if row[0].startswith("#") or row[0].startswith("Name") or row[0] == '' or row[0].startswith('-'):
        continue
    print(row)

    if row[0].startswith("B"):
        bname = row[0].strip().replace("–", "-")
        pid = list(query['PSRB']).index(bname)
        pulsar = query['PSRJ'][pid]
    else:
        pulsar = row[0].strip().replace("–", "-")
    # Wrong names I found
    if pulsar == "J1238+21":
        pulsar = "J1238+2152"

    if row[3] == '<':
        continue
    flux = float(row[4])
    flux_err = float(row[5])
    freq = round((float(row[1])+float(row[2]))/2,2)
    band = round((float(row[2])-float(row[1])),2)
    pulsar_dict[pulsar] = {
        "Frequency MHz":[freq],
        "Bandwidth MHz":[band],
        "Flux Density mJy":[flux],
        "Flux Density error mJy":[flux_err]
    }

with open("Bilous_2020.yaml", "w") as cat_file:
    yaml.safe_dump(pulsar_dict, cat_file, sort_keys=False, indent=2)