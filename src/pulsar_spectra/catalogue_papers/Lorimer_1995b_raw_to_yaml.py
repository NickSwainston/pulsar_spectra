import yaml
import psrqpy
import csv

with open("Lorimer_1995b_raw.tsv") as file:
    tsv_file = csv.reader(file, delimiter="\t")
    lines = []
    for line in tsv_file:
        lines.append(line)
query = psrqpy.QueryATNF(params=['PSRJ', 'NAME', 'PSRB']).pandas
print(lines)
print(list(query['PSRB']))

pulsar_dict = {}
for row in lines[48:]:
    row = [r.strip() for r in row]
    if row[0].startswith("#"):
        continue
    print(row)

    pulsar = row[0].strip().replace("–", "-")
    if pulsar == "1830-10":
        pulsar = "J" + pulsar
    elif pulsar == "1828-10":
        # this might not be right but couldn't find a better fit
        pulsar = "J1830-1059"
    else:
        bname = "B" + pulsar
        pid = list(query['PSRB']).index(bname)
        pulsar = query['PSRJ'][pid]

    pulsar_dict[pulsar] = {
        "Frequency MHz":[],
        "Bandwidth MHz":[],
        "Flux Density mJy":[],
        "Flux Density error mJy":[]
    }

    if row[1] != "" and row[2] != "":
        pulsar_dict[pulsar]["Frequency MHz"] += [408]
        pulsar_dict[pulsar]["Bandwidth MHz"] += [0.125]
        pulsar_dict[pulsar]["Flux Density mJy"] += [float(row[1])]
        pulsar_dict[pulsar]["Flux Density error mJy"] += [float(row[2])]

    if row[3] != "" and row[4] != "":
        pulsar_dict[pulsar]["Frequency MHz"] += [606]
        pulsar_dict[pulsar]["Bandwidth MHz"] += [0.250]
        pulsar_dict[pulsar]["Flux Density mJy"] += [float(row[3])]
        pulsar_dict[pulsar]["Flux Density error mJy"] += [float(row[4])]

    if row[5] != "" and row[6] != "":
        pulsar_dict[pulsar]["Frequency MHz"] += [925]
        pulsar_dict[pulsar]["Bandwidth MHz"] += [0.250]
        pulsar_dict[pulsar]["Flux Density mJy"] += [float(row[5])]
        pulsar_dict[pulsar]["Flux Density error mJy"] += [float(row[6])]

    if row[7] != "" and row[8] != "":
        pulsar_dict[pulsar]["Frequency MHz"] += [1408]
        pulsar_dict[pulsar]["Bandwidth MHz"] += [1]
        pulsar_dict[pulsar]["Flux Density mJy"] += [float(row[7])]
        pulsar_dict[pulsar]["Flux Density error mJy"] += [float(row[8])]

    if row[9] != "" and row[10] != "":
        pulsar_dict[pulsar]["Frequency MHz"] += [1606]
        pulsar_dict[pulsar]["Bandwidth MHz"] += [1]
        pulsar_dict[pulsar]["Flux Density mJy"] += [float(row[9])]
        pulsar_dict[pulsar]["Flux Density error mJy"] += [float(row[10])]

with open("Lorimer_1995b.yaml", "w") as cat_file:
    yaml.safe_dump(pulsar_dict, cat_file, sort_keys=False, indent=2)