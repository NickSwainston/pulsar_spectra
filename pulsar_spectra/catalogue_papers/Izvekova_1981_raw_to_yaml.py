#Izvekova_1981
import json
import psrqpy
import csv
import numpy as np

# was converted from image to csv using ABBYY FineReader
with open("Izvekova_1981_raw.csv") as file:
    tsv_file = csv.reader(file, delimiter=",")
    lines = []
    for line in tsv_file:
        lines.append(line)
query = psrqpy.QueryATNF(params=['PSRJ', 'NAME', 'PSRB', 'P0']).pandas
print(lines)
for i in list(query['PSRB']):
    if isinstance(i, str):
        print(i)

pulsar_dict = {}
for row in lines[2:]:
    row = [r.strip() for r in row]
    if row[0].startswith("#"):
        continue
    print(row)

    if "+" in row[1] or "-" in row[1]:
        pulsar = row[1].strip().replace("–", "-").replace(" ", "")
        bname = "B" + pulsar
        if bname == "B0012+47":
            bname = "B0011+47"
        if bname == "B0153+61":
            bname = "B0154+61"
        if bname == "B0340+53":
            bname = "B0339+53"
        if bname == "B0459+47":
            bname = "B0458+46"
        if bname == "B0752+32":
            bname = "B0751+32"
        if bname == "B09504-08":
            bname = "B0950+08"
        if bname == "B1905+40":
            bname = "B1905+39"
        if bname == "B1927+18":
            bname = "B1926+18"
        if bname == "B1954+51":
            bname = "B1953+50"
        if bname == "B2223+65":
            bname = "B2224+65"
        if bname == "B2305+55":
            bname = "B2306+55"
        pid = list(query['PSRB']).index(bname)
        pulsar = query['PSRJ'][pid]

        if pulsar not in pulsar_dict.keys():
            pulsar_dict[pulsar] = {"Frequency MHz":[],
                                   "Flux Density mJy":[],
                                   "Flux Density error mJy":[]}

    if not ("^" in row[3] or "<" in row[3]):
        pulsar_dict[pulsar]["Frequency MHz"] += [float(row[2])]
        flux, flux_err = row[3].replace("*", "").replace(" ", "").replace("+", "±").split("±")
        # 10^-29Jm^-2Hz^-1 = mJys
        pulsar_dict[pulsar]["Flux Density mJy"] += [float(flux)*1e3/query['P0'][pid]]
        pulsar_dict[pulsar]["Flux Density error mJy"] += [float(flux_err)*1e3/query['P0'][pid]]

with open("Izvekova_1981.yaml", "w") as cat_file:
    cat_file.write(json.dumps(pulsar_dict, indent=1))
print(pulsar_dict)