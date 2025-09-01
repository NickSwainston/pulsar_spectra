import numpy as np
import yaml

raw = np.loadtxt("Han_2016_raw.txt", dtype=str)

pulsar_dict = {}
for row in raw[1:]:
    pulsar = row[0]
    freqs = [float(row[2]), float(row[5]), float(row[8]), float(row[11])]
    bands = [64, 64, 64, 64]
    pairs = [row[4], row[7], row[10], row[13]]
    fluxs = []
    flux_errs = []
    for p in pairs:
        flux, flux_err = p.split("±")
        fluxs.append(float(flux))
        flux_errs.append(float(flux_err))

    pulsar_dict[pulsar] = {
        "Frequency MHz":freqs,
        "Bandwidth MHz":bands,
        "Flux Density mJy":fluxs,
        "Flux Density error mJy":flux_errs
    }

with open("Han_2016.yaml", "w") as cat_file:
    yaml.safe_dump(pulsar_dict, cat_file, sort_keys=False, indent=2)