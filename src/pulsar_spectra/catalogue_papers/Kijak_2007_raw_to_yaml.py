import json
import psrqpy

with open("Kijak_2007_raw.txt", "r") as raw_file:
    lines = raw_file.readlines()
query = psrqpy.QueryATNF(params=['PSRJ', 'NAME', 'PSRB']).pandas

pulsar_dict = {}
for row in lines:
    row = row.replace(" ± ", "±").split()
    print(row)
    if len(row) == 6:
        bname = row[0].replace("−", "-")
        pid = list(query['PSRB']).index(bname)
        pulsar = query['PSRJ'][pid]
        pulsar_dict[pulsar] = {
            "Frequency MHz":[],
            "Bandwidth MHz":[],
            "Flux Density mJy":[],
            "Flux Density error mJy":[]
        }
    freq = float(row[-4])
    if ">" not in row[-2]:
        flux, flux_err = row[-2].split("±")
        pulsar_dict[pulsar]["Frequency MHz"] += [freq]
        pulsar_dict[pulsar]["Bandwidth MHz"] += [16]
        pulsar_dict[pulsar]["Flux Density mJy"] += [float(flux)]
        pulsar_dict[pulsar]["Flux Density error mJy"] += [float(flux_err)]

json = json.dumps(pulsar_dict, indent=1)
with open("Kijak_2007.yaml", "w") as cat_file:
    cat_file.write(json)
print(pulsar_dict)