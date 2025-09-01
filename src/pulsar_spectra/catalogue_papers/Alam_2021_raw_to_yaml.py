import csv
import yaml

import psrqpy

query = psrqpy.QueryATNF(params=["PSRJ", "NAME", "PSRB", "P0"]).pandas
all_jnames = list(query["PSRJ"])

with open("Alam_2021_raw.csv") as file:
    tsv_file = csv.reader(file, delimiter=" ")
    lines = []
    for line in tsv_file:
        lines.append(line)

pulsars = [
    (430.0, 3),
    (820.0, 6),
    (1400.0, 9),
    (2100.0, 12),
]

pulsar_dict = {}
for row in lines:
    row = [r.strip() for r in row]

    pulsar = row[0].strip().replace("–", "-").replace(" ", "").replace("−", "-")
    if pulsar.startswith("B"):
        pid = list(query["PSRB"]).index(pulsar)
        pulsar = query["PSRJ"][pid]

    # Incorrect names
    if pulsar == "J1804-2718":
        pulsar = "J1804-2717"
    if pulsar == "J2129-5718":
        pulsar = "J2129-5721"
    if pulsar not in all_jnames:
        print(pulsar)

    pulsar_dict[pulsar] = {
        "Frequency MHz": [],
        "Bandwidth MHz": [],
        "Flux Density mJy": [],
        "Flux Density error mJy": [],
    }
    for freq, row_id in pulsars:
        if "L" in row[row_id]:
            continue
        flux = float(row[row_id])
        flux_err_lower = flux - float(row[row_id - 1])
        flux_err_upper = float(row[row_id + 1]) - flux
        flux_err_lower_rel = flux_err_lower / flux
        flux_err_upper_rel = flux_err_upper / flux

        if abs(flux_err_lower_rel - flux_err_upper_rel) < 0.2:
            # If the relative +/- uncertatinties are within 20% of each other
            # then average them to make them symmetical
            flux_err_rel = (flux_err_lower_rel + flux_err_upper_rel) / 2
            print(f"PSR {row[0]}: Symmetrical {flux_err_rel * 100:.2f}%")
        elif flux_err_lower_rel < 0.5 and flux_err_upper_rel < 0.5:
            # Take the larger of the two relative uncertainties
            flux_err_rel = max([flux_err_lower_rel, flux_err_upper_rel])
            print(f"PSR {row[0]}: Larger {flux_err_rel * 100:.2f}%")
        else:
            # If either side is >50% uncertainty, clip
            flux_err_rel = 0.5
            print(f"PSR {row[0]}: Clip +{flux_err_upper_rel * 100:.2f}% -{flux_err_lower_rel * 100:.2f}%")

        pulsar_dict[pulsar]["Frequency MHz"] += [freq]
        pulsar_dict[pulsar]["Bandwidth MHz"] += [64.0]
        pulsar_dict[pulsar]["Flux Density mJy"] += [round(flux, 2)]
        pulsar_dict[pulsar]["Flux Density error mJy"] += [round(flux * flux_err_rel, 2)]

with open("Alam_2021.yaml", "w") as cat_file:
    yaml.safe_dump(pulsar_dict, cat_file, sort_keys=False, indent=2)
