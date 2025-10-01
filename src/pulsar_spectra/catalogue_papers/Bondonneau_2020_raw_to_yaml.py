import yaml

from pulsar_spectra.scripts.csv_to_yaml import dump_yaml

with open("Bondonneau_2020_raw.txt", "r") as raw_file:
    lines = raw_file.readlines()
    print(lines)

pulsar_dict = {
    "Paper Metadata": {
        "Data Type": "Beamforming",
        "Observation Span": "Single-epoch",
    }
}
for row in lines:
    row = row.replace("()", "").replace("(τ)", "").split()
    print(row)
    pulsar = row[0].replace("–", "-").replace("−", "-")
    flux, flux_err = row[10].split("(")
    freq = float(row[8])
    if freq == 65.:
        band = 30
    else:
        band = 55
    # Wrong names I found
    if pulsar == "J0927+23":
        pulsar = "J0927+2345"

    pulsar_dict[pulsar] = {
        "Frequency MHz":[freq],
        "Bandwidth MHz":[band],
        "Flux Density mJy":[float(flux)],
        "Flux Density error mJy":[float(flux_err[:-1])]
    }

dump_yaml(pulsar_dict, "Bondonneau_2020.yaml")