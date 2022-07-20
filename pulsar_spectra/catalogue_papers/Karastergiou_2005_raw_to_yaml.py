import json

with open("Karastergiou_2005_raw.csv", "r") as raw_file:
    lines = raw_file.readlines()

pulsar_dict = {}
for row in lines:
    row = row.split(",")
    print(row)
    pulsar = row[0].replace("–", "-")

    pulsar_dict[pulsar] = {"Frequency MHz":[3100],
                           "Flux Density mJy":[float(row[3])],
                           # Text doesn't mention uncertainty so assuming 50%
                           "Flux Density error mJy":[float(row[3])*0.5]}

    if row[2] != "":
        pulsar_dict[pulsar]["Frequency MHz"] += [1400]
        pulsar_dict[pulsar]["Flux Density mJy"] += [float(row[2])]
        pulsar_dict[pulsar]["Flux Density error mJy"] += [float(row[2])*0.5]

with open("Karastergiou_2005.yaml", "w") as cat_file:
    cat_file.write(json.dumps(pulsar_dict, indent=1))
print(pulsar_dict)