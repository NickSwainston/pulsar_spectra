import yaml
import csv

with open("Lorimer_2006_raw.tsv", "r") as raw_file:
    tsv_file = csv.reader(raw_file, delimiter="\t")
    lines = []
    for line in tsv_file:
        lines.append(line)
    print(lines)

pulsar_dict = {}
for row in lines:
    row = [r.strip() for r in row]
    if len(row) == 0:
        continue
    if row[0].startswith("#") or row[0].startswith("PSR") or row[0] == '' or row[0].startswith('-'):
        continue
    print(row)

    pulsar = "J" + row[0].strip().replace("–", "-")

    flux = float(row[1])
    flux_err = flux * 0.5
    pulsar_dict[pulsar] = {
        "Frequency MHz":[1400],
        "Bandwidth MHz":[288],
        "Flux Density mJy":[flux],
        "Flux Density error mJy":[flux_err]
    }

with open("Lorimer_2006.yaml", "w") as cat_file:
    yaml.safe_dump(pulsar_dict, cat_file, sort_keys=False, indent=2)