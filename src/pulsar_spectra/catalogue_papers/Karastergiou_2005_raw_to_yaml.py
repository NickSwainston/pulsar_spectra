import yaml
import psrqpy

query = psrqpy.QueryATNF(params=['PSRJ', 'NAME', 'PSRB']).pandas
all_jnames = list(query['PSRJ'])

with open("Karastergiou_2005_raw.csv", "r") as raw_file:
    lines = raw_file.readlines()

pulsar_dict = {}
for row in lines:
    row = row.split(",")
    pulsar = row[0].replace("–", "-").replace("—", "-").replace("-", "-").strip()
    # Wrong names I found
    if "\ufeffJ1012-5857" in pulsar:
        pulsar = "J1012-5857"
    if pulsar not in all_jnames:
        print(pulsar)
        print(len(pulsar))

    pulsar_dict[pulsar] = {
        "Frequency MHz":[3100],
        "Bandwidth MHz":[1024],
        "Flux Density mJy":[float(row[3])],
        # Text doesn't mention uncertainty so assuming 50%
        "Flux Density error mJy":[float(row[3])*0.5]
    }

with open("Karastergiou_2005.yaml", "w") as cat_file:
    yaml.safe_dump(pulsar_dict, cat_file, sort_keys=False, indent=2)