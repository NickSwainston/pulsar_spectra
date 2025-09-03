import csv
import yaml

import psrqpy

query = psrqpy.QueryATNF(params=["PSRJ", "NAME", "PSRB", "P0"]).pandas
all_jnames = list(query["PSRJ"])

# was converted from image to csv using ABBYY FineReader
with open("Levin_2016_raw.txt") as file:
    pulsar_dict = {}

    spamreader = csv.reader(file, delimiter="\t")
    # Skip the header
    next(spamreader)
    next(spamreader)

    for row in spamreader:
        pulsar = row[0].strip()
        S1400 = row[3].strip()

        if pulsar.startswith("B"):
            pid = list(query["PSRB"]).index(pulsar)
            pulsar = query["PSRJ"][pid]

        if pulsar not in all_jnames:
            print(f"{pulsar} not in the ANTF")
            continue

        freqs = []
        bands = []
        fluxes = []
        flux_errs = []

        if S1400 != "":
            freqs.append(1500.0)
            bands.append(800.0)
            fluxes.append(float(S1400))
            flux_errs.append(float(S1400) * 0.5)

        pulsar_dict[pulsar] = {
            "Frequency MHz": freqs,
            "Bandwidth MHz": bands,
            "Flux Density mJy": fluxes,
            "Flux Density error mJy": flux_errs,
        }

with open("Levin_2016.yaml", "w") as cat_file:
    yaml.safe_dump(pulsar_dict, cat_file, sort_keys=False, indent=2)
