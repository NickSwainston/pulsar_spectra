import yaml

from pulsar_spectra.scripts.csv_to_yaml import dump_yaml

with open("Johnston_2006_raw.txt", "r") as raw_file:
    lines = raw_file.readlines()

pulsar_dict = {
    "Paper Metadata": {
        "Data Type": "Beamforming",
        "Observation Span": "Single-epoch",
    }
}
for row in lines:
    row = row.replace(" ± ", "±").split()
    print(row)
    pulsar = row[0].replace("–", "-").replace("−", "-")
    if pulsar == "J1327-6222":
        continue
    flux = float(row[4].split("(")[0])

    pulsar_dict[pulsar] = {
        "Frequency MHz":[8356],
        "Bandwidth MHz":[512],
        "Flux Density mJy":[flux],
        # Text doesn't mention uncertainty so assuming 50%
        "Flux Density error mJy":[flux*0.5]
        }

dump_yaml(pulsar_dict, "Johnston_2006.yaml")