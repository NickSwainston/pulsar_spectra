import json
from astroquery.vizier import Vizier

with open("Jankowski_2018_raw.txt", "r") as raw_file:
    lines = raw_file.readlines()
    print(lines)

pulsar_dict = {}
for row in lines[3:]:
    row = row.split("|")
    print(row)
    pulsar = row[0].strip().replace("−", "-")
    freqs = []
    fluxs = []
    flux_errs = []
    # If no error means it's an upper limit andnow sure how to handle it
    if row[1].strip() != "" and row[2].strip() != "":
        freqs.append(728)
        fluxs.append(float(row[1].strip()))
        flux_errs.append(float(row[2].strip()))
    if row[3].strip() != "" and row[4].strip() != "":
        freqs.append(1382)
        fluxs.append(float(row[3].strip()))
        flux_errs.append(float(row[4].strip()))
    if row[5].strip() != "" and row[6].strip() != "":
        freqs.append(3100)
        fluxs.append(float(row[5].strip()))
        flux_errs.append(float(row[6].strip()))
    pulsar_dict[pulsar] = {"Frequency MHz":freqs, "Flux Density mJy":fluxs, "Flux Density error mJy":flux_errs}

with open("Jankowski_2018.json", "w") as cat_file:
    cat_file.write(json.dumps(pulsar_dict))
print(pulsar_dict)