import yaml
from astroquery.vizier import Vizier

with open("Jankowski_2018_raw.txt", "r") as raw_file:
    lines = raw_file.readlines()
    print(lines)

pulsar_dict = {}
for row in lines[3:]:
    row = row.split("|")
    print(row)
    pulsar = row[0].strip().replace("−", "-")
    # wrong names I've found
    if pulsar == "J1235-5516":
        pulsar = "J1235-54"

    freqs = []
    bands = []
    fluxs = []
    flux_errs = []
    # If no error means it's an upper limit andnow sure how to handle it
    if row[1].strip() != "" and row[2].strip() != "":
        freqs.append(728)
        bands.append(64)
        fluxs.append(float(row[1].strip()))
        flux_errs.append(float(row[2].strip()))
    if row[3].strip() != "" and row[4].strip() != "":
        freqs.append(1382)
        bands.append(400)
        fluxs.append(float(row[3].strip()))
        flux_errs.append(float(row[4].strip()))
    if row[5].strip() != "" and row[6].strip() != "":
        freqs.append(3100)
        bands.append(1024)
        fluxs.append(float(row[5].strip()))
        flux_errs.append(float(row[6].strip()))
    pulsar_dict[pulsar] = {
        "Frequency MHz":freqs,
        "Bandwidth MHz":bands,
        "Flux Density mJy":fluxs,
        "Flux Density error mJy":flux_errs
        }

with open("Jankowski_2018.yaml", "w") as cat_file:
    yaml.safe_dump(pulsar_dict, cat_file, sort_keys=False, indent=2)