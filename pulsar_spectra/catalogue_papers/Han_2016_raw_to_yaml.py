import numpy as np
import json

raw = np.loadtxt("Han_2016_raw.txt", dtype=str)

pulsar_dict = {}
for row in raw[1:]:
    pulsar = row[0]
    freqs = [float(row[2]), float(row[5]), float(row[8])]
    pairs = [row[4], row[7], row[10]]
    fluxs = []
    flux_errs = []
    for p in pairs:
        flux, flux_err = p.split("±")
        fluxs.append(float(flux))
        flux_errs.append(float(flux_err))

    pulsar_dict[pulsar] = {"Frequency MHz":freqs, "Flux Density mJy":fluxs, "Flux Density error mJy":flux_errs}
json = json.dumps(pulsar_dict)
with open("Han_2016.yaml", "w") as cat_file:
    cat_file.write(json)
print(pulsar_dict)