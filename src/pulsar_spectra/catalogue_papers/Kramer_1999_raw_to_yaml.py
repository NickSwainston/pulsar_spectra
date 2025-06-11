import json
import psrqpy
import csv

query = psrqpy.QueryATNF(params=['PSRJ', 'NAME', 'PSRB', 'P0']).pandas
all_jnames = list(query['PSRJ'])

# was converted from image to csv using ABBYY FineReader
with open("Kramer_1999_raw.csv") as file:
    tsv_file = csv.reader(file, delimiter=" ")
    lines = []
    for line in tsv_file:
        lines.append(line)

pulsar_dict = {}
for row in lines:
    row = [r.strip() for r in row]

    pulsar = row[0].strip().replace("–", "-").replace(" ", "").replace("−", "-")
    # Wrong names
    if pulsar == "B1640+2224":
        pulsar = "J1640+2224"

    if pulsar.startswith("B"):
        pid = list(query['PSRB']).index(pulsar)
        pulsar = query['PSRJ'][pid]

    if pulsar not in all_jnames:
        print(pulsar)

    pulsar_dict[pulsar] = {
        "Frequency MHz":[],
        "Bandwidth MHz":[],
        "Flux Density mJy":[],
        "Flux Density error mJy":[]
    }

    if row[4] == "^":
        flux= float(row[3])
        flux_err = float(row[5])
        pulsar_dict[pulsar]["Frequency MHz"].append(2695.)
        pulsar_dict[pulsar]["Bandwidth MHz"].append(80.)
        pulsar_dict[pulsar]["Flux Density mJy"].append(flux)
        pulsar_dict[pulsar]["Flux Density error mJy"].append(flux_err)

    if row[7] == "^":
        flux= float(row[6])
        flux_err = float(row[8])
        pulsar_dict[pulsar]["Frequency MHz"].append(4850.)
        pulsar_dict[pulsar]["Bandwidth MHz"].append(80.)
        pulsar_dict[pulsar]["Flux Density mJy"].append(flux)
        pulsar_dict[pulsar]["Flux Density error mJy"].append(flux_err)


with open("Kramer_1999.yaml", "w") as cat_file:
    cat_file.write(json.dumps(pulsar_dict, indent=1))