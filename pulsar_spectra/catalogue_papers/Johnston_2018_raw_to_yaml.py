import json
import csv

with open("Johnston_2018_raw.tsv") as file:
    tsv_file = csv.reader(file, delimiter="\t")
    lines = []
    for line in tsv_file:
        lines.append(line)
print(lines)

pulsar_dict = {}
for row in lines:
    row = [r.strip() for r in row]
    if len(row) == 0:
        continue
    if row[0].startswith("#") or row[0].startswith("Name") or row[0] == '' or row[0].startswith('-') or row[1] == '':
        continue
    print(row)

    pulsar = row[0].strip().replace("–", "-")

    pulsar_dict[pulsar] = {"Frequency MHz":[1400],
                            "Flux Density mJy":[round(float(row[1]),1)],
                            "Flux Density error mJy":[round(float(row[1])*.2,1)]}

with open("Johnston_2018.yaml", "w") as cat_file:
    cat_file.write(json.dumps(pulsar_dict, indent=1))
print(pulsar_dict)