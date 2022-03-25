import json
import csv

with open("Hobbs_2004_raw.tsv") as file:
    tsv_file = csv.reader(file, delimiter="\t")
    lines = []
    for line in tsv_file:
        lines.append(line)
print(lines)

pulsar_dict = {}
for row in lines[39:320]:
    row = [r.strip() for r in row]
    if row[0].startswith("#"):
        continue
    print(row)

    pulsar = row[0].strip().replace("–", "-")

    if '' != row[1]:
        pulsar_dict[pulsar] = {"Frequency MHz":[1400],
                               "Flux Density mJy":[float(row[1])],
                               "Flux Density error mJy":[float(row[2])]}

for row in lines[369:]:
    row = [r.strip() for r in row]
    if row[0].startswith("#"):
        continue
    print(row)

    pulsar = row[0].strip().replace("–", "-")

    pulsar_dict[pulsar] = {"Frequency MHz":[1400],
                           "Flux Density mJy":[float(row[1])],
                           "Flux Density error mJy":[float(row[2])]}
    
    # "Taking a typical uncertainty of 10 per cent leads to an error in the spectral index determination of ∼ 0.3"
    if '' != row[3]:
        pulsar_dict[pulsar]["Frequency MHz"] += [400]
        pulsar_dict[pulsar]["Flux Density mJy"] += [float(row[3])]
        pulsar_dict[pulsar]["Flux Density error mJy"] += [round(float(row[3]) * 0.1, 4)]

    if '' != row[4]:
        pulsar_dict[pulsar]["Frequency MHz"] += [600]
        pulsar_dict[pulsar]["Flux Density mJy"] += [float(row[4])]
        pulsar_dict[pulsar]["Flux Density error mJy"] += [round(float(row[4]) * 0.1, 4)]

with open("Hobbs_2004.json", "w") as cat_file:
    cat_file.write(json.dumps(pulsar_dict))
print(pulsar_dict)