import csv
import yaml

import psrqpy

with open("Spiewak_2022_raw.csv") as file:
    tsv_file = csv.reader(file, delimiter=" ")
    lines = []
    for line in tsv_file:
        lines.append(line)
print(lines)

query = psrqpy.QueryATNF(params=["PSRJ", "NAME", "PSRB"]).pandas
all_jnames = list(query["PSRJ"])
# print(query['PSRB'])

pulsar_dict = {}
for row in lines:
    row = [r.strip() for r in row]
    # print(row)

    pulsar = row[0].strip().replace("–", "-").replace("∗", "")

    if pulsar not in all_jnames:
        print(pulsar)

    flux, flux_err = row[9].split("(")
    sig_fig = len(flux.split(".")[-1])
    flux = float(flux)
    flux_err = round(float(flux_err[:-1]) * 10 ** (-sig_fig), sig_fig)
    pulsar_dict[pulsar] = {
        "Frequency MHz": [1284],
        "Bandwidth MHz": [775.75],
        "Flux Density mJy": [flux],
        "Flux Density error mJy": [flux_err],
    }

with open("Spiewak_2022.yaml", "w") as cat_file:
    yaml.safe_dump(pulsar_dict, cat_file, sort_keys=False, indent=2)
