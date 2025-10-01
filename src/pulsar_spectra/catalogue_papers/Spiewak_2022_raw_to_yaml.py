import csv
import yaml

import psrqpy

from pulsar_spectra.scripts.csv_to_yaml import dump_yaml

with open("Spiewak_2022_raw.csv") as file:
    tsv_file = csv.reader(file, delimiter=" ")
    lines = []
    for line in tsv_file:
        lines.append(line)

# Gitika et al. (2023) provide updated and band-resolved flux densities from MeerKAT
# monitoring observations of the 88 MPTA MSPs. For these MSPs, the Spiewak et al. (2022)
# flux densities are redundant and less informative as they are band-averaged. We
# therefore exclude them from the catalogue.
with open("Gitika_2023.yaml", "r") as cat_file:
    gitika_dict = yaml.safe_load(cat_file)

query = psrqpy.QueryATNF(params=["PSRJ", "NAME", "PSRB"]).pandas
all_jnames = list(query["PSRJ"])
# print(query['PSRB'])

pulsar_dict = {
    "Paper Metadata": {
        "Data Type": "Beamforming",
        "Observation Span": "Single-epoch",
    }
}
for row in lines:
    row = [r.strip() for r in row]
    # print(row)

    pulsar = row[0].strip().replace("–", "-").replace("∗", "")

    if pulsar not in all_jnames:
        print(pulsar)

    if pulsar in gitika_dict.keys():
        print(f"PSR {pulsar} is in Gitika_2023")
        continue

    flux, flux_err = row[9].split("(")
    sig_fig = len(flux.split(".")[-1])
    flux = float(flux)
    flux_err = round(float(flux_err[:-1]) * 10 ** (-sig_fig), sig_fig)
    pulsar_dict[pulsar] = {
        "Frequency MHz": [1284.0],
        "Bandwidth MHz": [775.75],
        "Flux Density mJy": [flux],
        "Flux Density error mJy": [flux_err],
    }

dump_yaml(pulsar_dict, "Spiewak_2022.yaml")
