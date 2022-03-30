import json
import psrqpy

with open("Zakharenko_2013_raw.txt", "r") as raw_file:
    lines = raw_file.readlines()
query = psrqpy.QueryATNF(params=['PSRJ', 'NAME', 'PSRB']).pandas

pulsar_dict = {}
for row in lines[:15]:
    row = row.replace(" ± ", "±").split(" ")
    print(row)
    bname = row[1].replace("−", "-")
    pid = list(query['PSRB']).index(bname)
    pulsar = query['PSRJ'][pid]

    freq = float(row[-2][1:])
    flux, flux_err = row[5].split("±")
    pulsar_dict[pulsar] = {"Frequency MHz":[20, 25, freq],
                           "Flux Density mJy":[float(row[2]), float(row[3]), float(flux)],
                           "Flux Density error mJy":[float(row[7][1:]), float(row[8][1:]), float(flux_err.replace("*", ""))]}


for row in lines[16:]:
    row = row.replace(" ± ", "±").split(" ")
    print(row)
    if row[1].startswith("B"):
        bname = row[1].replace("−", "-")
        pid = list(query['PSRB']).index(bname)
        pulsar = query['PSRJ'][pid]
    else:
        pulsar = row[1].replace("−", "-")

    flux, flux_err = row[2].split("±")
    pulsar_dict[pulsar] = {"Frequency MHz":[25],
                           "Flux Density mJy":[float(flux)],
                           "Flux Density error mJy":[float(flux_err.replace("*", ""))]}

    if "±" in row[3]:
        freq = float(row[-2][1:])
        flux, flux_err = row[3].split("±")
        pulsar_dict[pulsar]["Frequency MHz"] += [float(freq)]
        pulsar_dict[pulsar]["Flux Density mJy"] += [float(flux)]
        pulsar_dict[pulsar]["Flux Density error mJy"] += [float(flux_err.replace("*", ""))]

json = json.dumps(pulsar_dict)
with open("Zakharenko_2013.yaml", "w") as cat_file:
    cat_file.write(json)
print(pulsar_dict)