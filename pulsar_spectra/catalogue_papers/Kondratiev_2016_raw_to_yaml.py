import json
import psrqpy
import csv

query = psrqpy.QueryATNF(params=['PSRJ', 'NAME', 'PSRB', 'P0']).pandas
all_jnames = list(query['PSRJ'])

# was converted from image to csv using ABBYY FineReader
with open("Kondratiev_2016_raw.csv") as file:
    tsv_file = csv.reader(file, delimiter=",")
    lines = []
    for line in tsv_file:
        lines.append(line)

pulsar_dict = {}
for row in lines:
    row = [r.strip() for r in row]

    pulsar = row[0].strip().replace("–", "-").replace(" ", "").replace("−", "-")
    if pulsar.startswith("B"):
        pid = list(query['PSRB']).index(pulsar)
        pulsar = query['PSRJ'][pid]

    flux, flux_err = row[4].split("(")
    if "." in flux:
        sig_fig = len(flux.split(".")[-1])
    else:
        sig_fig = 0
    flux = float(flux)
    flux_err = round(float(flux_err[:-1]) * 10**(-sig_fig), 1)

    pulsar_dict[pulsar] = {
        "Frequency MHz":[149.],
        "Bandwidth MHz":[78.],
        "Flux Density mJy":[flux],
        "Flux Density error mJy":[flux_err]
    }

with open("Kondratiev_2016.yaml", "w") as cat_file:
    cat_file.write(json.dumps(pulsar_dict, indent=1))