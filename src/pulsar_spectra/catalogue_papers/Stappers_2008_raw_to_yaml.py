import yaml
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
        "Frequency MHz":[147.5],
        "Bandwidth MHz":[60],
        "Flux Density mJy":[float(row[3])],
        "Flux Density error mJy":[float(row[4])],
    }


with open("Stappers_2008.yaml", "w") as cat_file:
    yaml.safe_dump(pulsar_dict, cat_file, sort_keys=False, indent=2)