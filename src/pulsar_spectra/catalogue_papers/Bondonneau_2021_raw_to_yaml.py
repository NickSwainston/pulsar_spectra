import yaml
import psrqpy
import csv

with open("Bondonneau_2021_raw.csv", "r") as file:
    tsv_file = csv.reader(file, delimiter=" ")
    lines = []
    for line in tsv_file:
        lines.append(line)
query = psrqpy.QueryATNF(params=['PSRJ', 'NAME', 'PSRB']).pandas
all_jnames = list(query['PSRJ'])

pulsar_dict = {}
for row in lines:
    row = [r.strip() for r in row]
    pulsar = row[0].strip().replace("–", "-").replace(" ", "").replace("−", "-").replace("*", "")
    if pulsar.startswith("B"):
        pid = list(query['PSRB']).index(pulsar)
        pulsar = query['PSRJ'][pid]

    # Wrong names I found
    if pulsar == "J1710+49":
        pulsar = "J1710+4923"
    if pulsar not in all_jnames:
        print(pulsar)

    flux, flux_err = row[4].split("(")
    flux = float(flux)
    flux_err = float(flux_err[:-1])
    pulsar_dict[pulsar] = {
        "Frequency MHz":[50],
        "Bandwidth MHz":[75],
        "Flux Density mJy":[flux],
        "Flux Density error mJy":[flux_err]
    }

with open("Bondonneau_2021.yaml", "w") as cat_file:
    yaml.safe_dump(pulsar_dict, cat_file, sort_keys=False, indent=2)