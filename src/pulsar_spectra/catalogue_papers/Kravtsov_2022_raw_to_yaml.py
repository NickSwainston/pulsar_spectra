import yaml
import psrqpy
import csv

query = psrqpy.QueryATNF(params=['PSRJ', 'NAME', 'PSRB', 'P0']).pandas
all_jnames = list(query['PSRJ'])

# was converted from image to csv using ABBYY FineReader
with open("Kravtsov_2022_raw.csv") as file:
    tsv_file = csv.reader(file, delimiter=" ")
    lines = []
    for line in tsv_file:
        lines.append(line)

pulsar_dict = {}
for row in lines:
    row = [r.strip() for r in row]

    pulsar = row[1].strip().replace("–", "-").replace(" ", "").replace("−", "-")
    if pulsar.startswith("B"):
        pid = list(query['PSRB']).index(pulsar)
        pulsar = query['PSRJ'][pid]
    # Wrong names
    if pulsar == "J0121+1":
        pulsar = "J0122+1416"
    if pulsar == "J0454+45":
        pulsar = "J0454+4529"
    if pulsar == "J2122+24":
        pulsar = "J2122+2426"
    if pulsar == "J2227+30":
        pulsar = "J2227+3038"
    if pulsar not in all_jnames:
        print(pulsar)

    flux = float(row[7])
    flux_err = float(row[9])

    pulsar_dict[pulsar] = {
        "Frequency MHz":[24.75],
        "Bandwidth MHz":[16.5],
        "Flux Density mJy":[flux],
        "Flux Density error mJy":[flux_err]
    }

with open("Kravtsov_2022.yaml", "w") as cat_file:
    yaml.safe_dump(pulsar_dict, cat_file, sort_keys=False, indent=2)