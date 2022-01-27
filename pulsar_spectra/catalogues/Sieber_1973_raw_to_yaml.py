import json
import psrqpy
import csv

# was converted from image to csv using ABBYY FineReader
with open("Sieber_1973_raw.csv") as file:
    tsv_file = csv.reader(file, delimiter=",")
    lines = []
    for line in tsv_file:
        lines.append(line)
query = psrqpy.QueryATNF(params=['PSRJ', 'NAME', 'PSRB', 'P0']).pandas
print(lines)
print(list(query['PSRB']))

pulsar_dict = {}
for row in lines[2:]:
    row = [r.strip() for r in row]
    if row[0].startswith("#"):
        continue
    print(row)

    if "PSR" in row[0]:
        pulsar = row[0].strip().replace("–", "-").replace(" ", "")[3:]
        bname = "B" + pulsar
        pid = list(query['PSRB']).index(bname)
        pulsar = query['PSRJ'][pid]

        if pulsar not in pulsar_dict.keys():
            pulsar_dict[pulsar] = {"Frequency MHz":[],
                                "Flux Density mJy":[],
                                "Flux Density error mJy":[]}

    if not (">" in row[3] or "<" in row[3] or "A" in row[1]):
        pulsar_dict[pulsar]["Frequency MHz"] += [float(row[2])]
        # 10^-29Jm^-2Hz^-1 = mJys
        if "m" in row[3]:
            flux = float(row[3][:-2])
        else:
            flux = float(row[3].replace("'", "").strip())
        # Remove the s term by dividing by the period
        pulsar_dict[pulsar]["Flux Density mJy"] += [flux/query['P0'][pid]]

        if "a" in row[4]:
            fact_err = 0.25
        elif "b" in row[4]:
            fact_err = 0.5
        elif "c" in row[4]:
            fact_err = 0.75
        pulsar_dict[pulsar]["Flux Density error mJy"] += [round(flux*fact_err, 3)]

with open("Sieber_1973.json", "w") as cat_file:
    cat_file.write(json.dumps(pulsar_dict))
print(pulsar_dict)