import yaml
import psrqpy
import csv

from pulsar_spectra.scripts.csv_to_yaml import dump_yaml

query = psrqpy.QueryATNF(params=['PSRJ', 'NAME', 'PSRB', 'P0']).pandas
all_jnames = list(query['PSRJ'])

pulsar_dict = {
    "Paper Metadata": {
        "Data Type": "Beamforming",
        "Observation Span": "Single-epoch",
    }
}

with open("Martsen_2022_raw.txt") as file:
    tsv_file = csv.reader(file, delimiter=" ")
    lines = []
    for line in tsv_file:
        lines.append(line)

for row in lines:
    if row[0].startswith("#") or row[0].strip() == "":
        continue
    row = [r.strip() for r in row]

    pulsar = "J1748-2446" + row[0].strip().replace("–", "-").replace(" ", "").replace("−", "-")

    if pulsar not in all_jnames:
        print(pulsar)

    pulsar_dict[pulsar] = {
        "Frequency MHz":[],
        "Bandwidth MHz":[],
        "Flux Density mJy":[],
        "Flux Density error mJy":[]
    }

    flux = float(row[4]) / 1000  # mJy
    # The table quotes a 5% error but also mentions that this is likely an underestimate so using 50 %
    # flux_err = flux * 0.05  # 5% error
    flux_err = flux * 0.5  # 50% error
    pulsar_dict[pulsar]["Frequency MHz"].append(1500.0)
    pulsar_dict[pulsar]["Bandwidth MHz"].append(650.0)
    pulsar_dict[pulsar]["Flux Density mJy"].append(round(flux, 4))
    pulsar_dict[pulsar]["Flux Density error mJy"].append(round(flux_err, 4))

    flux = float(row[5]) / 1000  # mJy
    # flux_err = flux * 0.2  # 20% error
    flux_err = flux * 0.5  # 50% error
    pulsar_dict[pulsar]["Frequency MHz"].append(2000.0)
    pulsar_dict[pulsar]["Bandwidth MHz"].append(650.0)
    pulsar_dict[pulsar]["Flux Density mJy"].append(round(flux, 4))
    pulsar_dict[pulsar]["Flux Density error mJy"].append(round(flux_err, 4))

dump_yaml(pulsar_dict, "Martsen_2022.yaml")