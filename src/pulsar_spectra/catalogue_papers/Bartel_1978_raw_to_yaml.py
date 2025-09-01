import yaml
import psrqpy
import csv

# was converted from image to csv using ABBYY FineReader
with open("Bartel_1978_raw.csv") as file:
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
    print(row)

    if "-" in row[1] or "+" in row[1]:
        pulsar = row[1].strip().replace("–", "-").replace(" ", "")
        bname = "B" + pulsar
        pid = list(query['PSRB']).index(bname)
        pulsar = query['PSRJ'][pid]

        if pulsar not in pulsar_dict.keys():
            pulsar_dict[pulsar] = {
                "Frequency MHz":[],
                "Bandwidth MHz":[],
                "Flux Density mJy":[],
                "Flux Density error mJy":[]
            }

    if not "<" in row[2]:
        pulsar_dict[pulsar]["Frequency MHz"] += [14800]
        pulsar_dict[pulsar]["Bandwidth MHz"] += [500]
        # 10^-29Jm^-2Hz^-1 = mJy

        if "mode" in row[2]:
            flux = 0.7
            flux_err = 0.4
        elif "±" in row[2]:
            flux, flux_err = row[2].split("±")
            flux = float(flux)
            flux_err = float(flux_err)
        else:
            flux = float(row[2])
            # no error mentioned so I assumed
            flux_err = flux * 0.5
        pulsar_dict[pulsar]["Flux Density mJy"] += [flux/query['P0'][pid]]
        pulsar_dict[pulsar]["Flux Density error mJy"] += [round(flux_err/query['P0'][pid], 3)]

    if not "<" in row[6]:
        pulsar_dict[pulsar]["Frequency MHz"] += [22700]
        pulsar_dict[pulsar]["Bandwidth MHz"] += [300]
        # 10^-29Jm^-2Hz^-1 = mJy

        if "±" in row[6]:
            flux, flux_err = row[6].split("±")
            flux = float(flux)
            flux_err = float(flux_err)
        pulsar_dict[pulsar]["Flux Density mJy"] += [flux]
        pulsar_dict[pulsar]["Flux Density error mJy"] += [round(flux_err, 3)]

with open("Bartel_1978.yaml", "w") as cat_file:
    yaml.safe_dump(pulsar_dict, cat_file, sort_keys=False, indent=2)