import yaml

with open("Johnston_2021_raw.txt", "r") as raw_file:
    lines = raw_file.readlines()
    print(lines)

pulsar_dict = {
    "Paper Metadata": {
        "Data Type": "Beamforming",
        "Observation Span": "Single-epoch",
    }
}
for row in lines[1:]:
    row = row.split()
    print(row)
    pulsar = row[0].replace("−", "-")
    flux = float(row[1])
    flux_err = float(row[2])
    pulsar_dict[pulsar] = {
        "Frequency MHz":[1369],
        "Bandwidth MHz":[256],
        "Flux Density mJy":[flux],
        "Flux Density error mJy":[flux_err]
    }

with open("Johnston_2021.yaml", "w") as cat_file:
    yaml.safe_dump(pulsar_dict, cat_file, sort_keys=False, indent=2)