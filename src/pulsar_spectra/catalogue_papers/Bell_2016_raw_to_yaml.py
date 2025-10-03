import yaml

from pulsar_spectra.scripts.csv_to_yaml import dump_yaml

with open("Bell_2016_raw.txt", "r") as raw_file:
    lines = raw_file.readlines()
    print(lines)

pulsar_dict = {
    "Paper Metadata": {
        "Data Type": "Imaging",
        "Observation Span": "Multi-epoch",
    }
}
for row in lines[1:]:
    row = row.replace(" ± ", "±").split(" ")
    pulsar = row[1].replace("−", "-")
    flux, flux_err = row[7].split("±")
    pulsar_dict[pulsar] = {
        "Frequency MHz":[154.],
        "Bandwidth MHz":[30.72],
        "Flux Density mJy":[float(flux)*1e3],
        "Flux Density error mJy":[float(flux_err)*1e3]
    }

dump_yaml(pulsar_dict, "Bell_2016.yaml")