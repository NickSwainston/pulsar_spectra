import yaml
import csv
import psrqpy

query = psrqpy.QueryATNF(params=['PSRJ', 'NAME', 'PSRB']).pandas
jnames = list(query['PSRJ'])

with open("Manchester_2001_raw.tsv", "r") as raw_file:
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
    #print(row)

    pulsar = "J" + row[0].strip().replace("–", "-")


    if pulsar not in jnames:
        print(pulsar)


    flux = float(row[1])
    flux_err = float(row[2]) * 0.01
    pulsar_dict[pulsar] = {
        "Frequency MHz":[1374.],
        "Bandwidth MHz":[288.],
        "Flux Density mJy":[flux],
        "Flux Density error mJy":[flux_err]
    }

with open("Manchester_2001.yaml", "w") as cat_file:
    yaml.safe_dump(pulsar_dict, cat_file, sort_keys=False, indent=2)