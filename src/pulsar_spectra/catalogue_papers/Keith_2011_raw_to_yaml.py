import yaml

with open("Keith_2011_raw.txt", "r") as raw_file:
    lines = raw_file.readlines()

pulsar_dict = {}
for row in lines[:16]:
    row = row.split()
    print(row)
    if len(row) == 12:
        pulsar = row[0].replace("−", "-").replace("–", "-")
        pulsar_dict[pulsar] = {
            "Frequency MHz":[],
            "Bandwidth MHz":[],
            "Flux Density mJy":[],
            "Flux Density error mJy":[]
        }
    freq = float(row[-9])*1e3
    flux = float(row[-7])
    pulsar_dict[pulsar]["Frequency MHz"] += [freq]
    pulsar_dict[pulsar]["Bandwidth MHz"] += [1024]
    pulsar_dict[pulsar]["Flux Density mJy"] += [flux]
    # Text says assume %20 uncertainty
    pulsar_dict[pulsar]["Flux Density error mJy"] += [round(flux*.2, 4)]

with open("Keith_2011.yaml", "w") as cat_file:
    yaml.safe_dump(pulsar_dict, cat_file, sort_keys=False, indent=2)