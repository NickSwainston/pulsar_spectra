"""
This script parses data from the MeerTime TPA Data Release. To use the script:
1. download and unzip the file `tpa_data.zip` from doi.org/10.5281/zenodo.8430591
2. run the script from within the `tpa_data/` directory, which contains `*.fluxtable` files
"""

import glob
import numpy as np
import yaml

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
        "Flux Density mJy": [float(round(avg_flux, 3))],
        "Flux Density error mJy": [float(round(std_flux, 3))],
    }

with open("Keith_2024.yaml", "w") as cat_file:
    yaml.safe_dump(pulsar_dict, cat_file, sort_keys=False, indent=2)
