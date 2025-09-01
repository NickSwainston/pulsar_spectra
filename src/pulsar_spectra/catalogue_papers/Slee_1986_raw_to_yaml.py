import csv
import yaml

import psrqpy

query = psrqpy.QueryATNF(params=["PSRJ", "NAME", "PSRB", "P0"]).pandas
all_jnames = list(query["PSRJ"])

# was converted from image to csv using ABBYY FineReader
with open("Slee_1986_raw.csv") as file:
    pulsar_dict = {}

    spamreader = csv.reader(file)
    # Skip the header
    next(spamreader)

    for row in spamreader:
        if len(row) == 3:
            pulsar, S80, S160 = row
        else:
            print(f"Error on row: {row}")

        pid = list(query["PSRB"]).index(pulsar)
        pulsar = query["PSRJ"][pid]

        if pulsar not in all_jnames:
            print(f"{pulsar} not in the ANTF")

        freqs = []
        bands = []
        fluxes = []
        flux_errs = []

        if S80 != "":
            freqs.append(80.0)
            bands.append(0.88)
            fluxes.append(float(S80))
            flux_errs.append(float(S80) * 0.5)

        if S160 != "":
            freqs.append(160.0)
            bands.append(0.88)
            fluxes.append(float(S160))
            flux_errs.append(float(S160) * 0.5)

        pulsar_dict[pulsar] = {
            "Frequency MHz": freqs,
            "Bandwidth MHz": bands,
            "Flux Density mJy": fluxes,
            "Flux Density error mJy": flux_errs,
        }

with open("Slee_1986.yaml", "w") as cat_file:
    yaml.safe_dump(pulsar_dict, cat_file, sort_keys=False, indent=2)
