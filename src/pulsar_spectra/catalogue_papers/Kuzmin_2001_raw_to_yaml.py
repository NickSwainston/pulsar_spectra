import yaml
import psrqpy
import csv

query = psrqpy.QueryATNF(params=['PSRJ', 'NAME', 'PSRB', 'P0']).pandas
all_jnames = list(query['PSRJ'])

# was converted from image to csv using ABBYY FineReader
with open("Kuzmin_2001_raw.csv") as file:
    tsv_file = csv.reader(file, delimiter=" ")
    lines = []
    for line in tsv_file:
        lines.append(line)

pulsar_dict = {}
for i, row in enumerate(lines):
    row = [r.strip() for r in row]

    pulsar = row[0].strip().replace("–", "-").replace(" ", "").replace("−", "-")
    if pulsar.startswith("B"):
        pid = list(query['PSRB']).index(pulsar)
        pulsar = query['PSRJ'][pid]

    # Incorrect names
    if pulsar == "J2033+1736":
        pulsar = "J2033+1734"
    if pulsar not in all_jnames:
        print(pulsar)

    if i < 30:
        pulsar_dict[pulsar] = {
            "Frequency MHz":[],
            "Bandwidth MHz":[],
            "Flux Density mJy":[],
            "Flux Density error mJy":[]
        }
        freq = float(row[4])
        pulsar_dict[pulsar]["Frequency MHz"].append(freq)
        pulsar_dict[pulsar]["Bandwidth MHz"].append(0.16)
    else:
        flux = float(row[1])
        flux_err = float(row[2])
        pulsar_dict[pulsar]["Flux Density mJy"].append(flux)
        pulsar_dict[pulsar]["Flux Density error mJy"].append(flux_err)

with open("Kuzmin_2001.yaml", "w") as cat_file:
    yaml.safe_dump(pulsar_dict, cat_file, sort_keys=False, indent=2)