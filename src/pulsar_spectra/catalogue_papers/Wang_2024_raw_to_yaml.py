import csv
import yaml

import psrqpy

query = psrqpy.QueryATNF(params=["PSRJ", "NAME", "PSRB", "P0"]).pandas
all_jnames = list(query["PSRJ"])

# was converted from image to csv using ABBYY FineReader
with open("Wang_2024_raw.txt") as file:
    pulsar_dict = {}

    spamreader = csv.reader(file, delimiter="\t")
    # Skip the header
    next(spamreader)
    next(spamreader)
    next(spamreader)

    for row in spamreader:
        pulsar = row[0].strip()

        if pulsar.startswith("B"):
            pid = list(query["PSRB"]).index(pulsar)
            pulsar = query["PSRJ"][pid]

        if pulsar not in all_jnames:
            print(f"{pulsar} not in the ANTF")
            continue

        # S band
        Sflux, Sflux_err = row[7].split("(")
        Ssig_fig = len(Sflux.split(".")[-1])
        Sflux = float(Sflux)
        Sflux_err = round(float(Sflux_err[:-1]) * 10 ** (-Ssig_fig), Ssig_fig)

        # X band
        Xflux, Xflux_err = row[8].split("(")
        Xsig_fig = len(Xflux.split(".")[-1])
        Xflux = float(Xflux)
        Xflux_err = round(float(Xflux_err[:-1]) * 10 ** (-Xsig_fig), Xsig_fig)

        pulsar_dict[pulsar] = {
            "Frequency MHz": [2250.0, 8600.0],
            "Bandwidth MHz": [100.0, 800.0],
            "Flux Density mJy": [Sflux, Xflux],
            "Flux Density error mJy": [Sflux_err, Xflux_err],
        }

with open("Wang_2024.yaml", "w") as cat_file:
    yaml.safe_dump(pulsar_dict, cat_file, sort_keys=False, indent=2)
