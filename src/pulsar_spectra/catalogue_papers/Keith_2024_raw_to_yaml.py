import glob
import numpy as np
import json

filenames = []
for filename in glob.iglob(f'*.fluxtable'):
    filenames.append(filename)

filenames.sort()

pulsar_dict = {}
for filename in filenames:
    psrj = filename.split(".")[0]

    mjd, flux, flux_err = np.loadtxt(filename, unpack=True, dtype=float)

    avg_flux = np.average(flux, weights=flux_err)
    std_flux = np.std(flux)

    pulsar_dict[psrj] = {
        "Frequency MHz": [1283.5],
        "Bandwidth MHz": [775.0],
        "Flux Density mJy": [round(avg_flux, 3)],
        "Flux Density error mJy": [round(std_flux, 3)],
    }

print(json.dumps(pulsar_dict, indent=4))
with open("Keith_2024.yaml", "w") as f:
    f.write(json.dumps(pulsar_dict, indent=1))