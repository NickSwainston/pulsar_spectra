import json
import psrqpy

with open("Stappers_2008_raw.txt", "r") as raw_file:
    lines = raw_file.readlines()
query = psrqpy.QueryATNF(params=['PSRJ', 'NAME', 'PSRB']).pandas

pulsar_dict = {}
for row in lines:
    row = row.split()
    print(row)

    if "B" in row[0]:
        pid = list(query['PSRB']).index(row[0])
        pulsar = query['PSRJ'][pid]
    else:
        pulsar = row[0]

    pulsar_dict[pulsar] = {
        "Frequency MHz":[147.5], # assumed from the bandwidth
        "Flux Density mJy":[float(row[3])],
        "Flux Density error mJy":[float(row[4])],
    }


with open("Stappers_2008.yaml", "w") as cat_file:
    cat_file.write(json.dumps(pulsar_dict, indent=1))
print(pulsar_dict)