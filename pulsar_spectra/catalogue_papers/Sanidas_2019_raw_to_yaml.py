import json
import csv
import psrqpy

with open("Sanidas_2019_raw.tsv") as file:
    tsv_file = csv.reader(file, delimiter="\t")
    lines = []
    for line in tsv_file:
        lines.append(line)
print(lines)

query = psrqpy.QueryATNF(params=['PSRJ', 'NAME', 'PSRB']).pandas
print(query['PSRB'])

pulsar_dict = {}
for row in lines:
    row = [r.strip() for r in row]
    if len(row) == 0:
        continue
    if row[0].startswith("#") or row[0].startswith("PSR") or row[0] == '' or row[0].startswith('-'):
        continue
    print(row)

    if row[0].startswith("B"):
        bname = row[0].strip().replace("–", "-")
        pid = list(query['PSRB']).index(bname)
        pulsar = query['PSRJ'][pid]
    else:
        pulsar = row[0].strip().replace("–", "-")
    pulsar_dict[pulsar] = {"Frequency MHz":[],
                            "Flux Density mJy":[],
                            "Flux Density error mJy":[]}

    for row_id, freq in [(1, 400), (2, 150)]:
        if row[row_id] != '':
            pulsar_dict[pulsar]["Frequency MHz"] += [freq]
            pulsar_dict[pulsar]["Flux Density mJy"] += [float(row[row_id])]
            pulsar_dict[pulsar]["Flux Density error mJy"] += [float(row[row_id])*0.5]
    if len(pulsar_dict[pulsar]["Frequency MHz"]) == 0:
        del pulsar_dict[pulsar]

with open("Sanidas_2019.yaml", "w") as cat_file:
    cat_file.write(json.dumps(pulsar_dict))
print(pulsar_dict)