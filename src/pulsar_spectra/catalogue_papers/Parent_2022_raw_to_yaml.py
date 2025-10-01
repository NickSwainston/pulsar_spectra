import yaml
import psrqpy
import csv

query = psrqpy.QueryATNF(params=['PSRJ', 'NAME', 'PSRB', 'P0']).pandas
all_jnames = list(query['PSRJ'])

pulsar_dict = {
    "Paper Metadata": {
        "Data Type": "Beamforming",
        "Observation Span": "Single-epoch",
    }
}

# TODO: Also add in the newly discovered pulsars from Parent+2022

with open("Parent_2022_raw_known.txt") as file:
    tsv_file = csv.reader(file, delimiter=" ")
    lines = []
    for line in tsv_file:
        lines.append(line)

for row in lines:
    if row[0].startswith("#") or row[0].strip() == "":
        continue
    row = [r.strip() for r in row]

    pulsar = row[0].strip().replace("–", "-").replace(" ", "").replace("−", "-")
    pulsar = pulsar.replace("a", "").replace("b", "")

    if pulsar not in all_jnames:
        print(pulsar)

    pulsar_dict[pulsar] = {
        "Frequency MHz":[],
        "Bandwidth MHz":[],
        "Flux Density mJy":[],
        "Flux Density error mJy":[]
    }

    flux, flux_err = row[6].split("(")
    if "." in flux:
        sig_fig = len(flux.split(".")[-1])
    else:
        sig_fig = 0
    flux = float(flux)
    flux_err = round(float(flux_err[:-1]) * 10**(-sig_fig), sig_fig)
    pulsar_dict[pulsar]["Frequency MHz"].append(1375.5)
    pulsar_dict[pulsar]["Bandwidth MHz"].append(323.0)
    pulsar_dict[pulsar]["Flux Density mJy"].append(flux/1000)  # Convert from uJy to mJy
    pulsar_dict[pulsar]["Flux Density error mJy"].append(flux_err/1000)  # Convert from uJy to mJy

with open("Parent_2022.yaml", "w") as cat_file:
    yaml.safe_dump(pulsar_dict, cat_file, sort_keys=False, indent=2)