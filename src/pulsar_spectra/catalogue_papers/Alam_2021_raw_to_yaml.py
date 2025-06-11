import json
import psrqpy
import csv

query = psrqpy.QueryATNF(params=['PSRJ', 'NAME', 'PSRB', 'P0']).pandas
all_jnames = list(query['PSRJ'])

with open("Alam_2021_raw.csv") as file:
    tsv_file = csv.reader(file, delimiter=" ")
    lines = []
    for line in tsv_file:
        lines.append(line)

pulsars = [
    (430, 3),
    (820, 6),
    (1400, 9),
    (2100, 12),
]

pulsar_dict = {}
for row in lines:
    row = [r.strip() for r in row]

    pulsar = row[0].strip().replace("–", "-").replace(" ", "").replace("−", "-")
    if pulsar.startswith("B"):
        pid = list(query['PSRB']).index(pulsar)
        pulsar = query['PSRJ'][pid]

    # Incorrect names
    if pulsar == "J1804-2718":
        pulsar = "J1804-2717"
    if pulsar == "J2129-5718":
        pulsar = "J2129-5721"
    if pulsar not in all_jnames:
        print(pulsar)

    pulsar_dict[pulsar] = {
        "Frequency MHz":[],
        "Bandwidth MHz":[],
        "Flux Density mJy":[],
        "Flux Density error mJy":[]
    }
    for freq, row_id in pulsars:
        if "L" in row[row_id]:
            continue
        flux = round(float(row[row_id]), 2)
        flux_err = round((float(row[row_id+1]) - float(row[row_id-1])) / 2, 2)
        if flux_err > flux/ 2:
            flux_err = round(flux / 2, 2)
        pulsar_dict[pulsar]["Frequency MHz"] += [freq]
        pulsar_dict[pulsar]["Bandwidth MHz"] += [64]
        pulsar_dict[pulsar]["Flux Density mJy"] += [flux]
        pulsar_dict[pulsar]["Flux Density error mJy"] += [flux_err]

with open("Alam_2021.yaml", "w") as cat_file:
    cat_file.write(json.dumps(pulsar_dict, indent=1))
#print(pulsar_dict)