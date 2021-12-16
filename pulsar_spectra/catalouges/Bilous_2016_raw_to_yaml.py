import json

with open("Bilous_2016_raw.txt", "r") as raw_file:
    lines = raw_file.readlines()
    print(lines)

pulsar_dict = {}
for row in lines:
    row = row.split()
    print(row)
    pulsar = row[1]
    flux = float(row[2])
    if len(row) == 3:
        flux_err = None
    else:
        flux_err = float(row[3])
    pulsar_dict[pulsar] = {"Frequency MHz":[150.], "Flux Density mJy":[flux], "Flux Density error mJy":[flux_err]}

with open("Bilous_2016.json", "w") as cat_file:
    cat_file.write(json.dumps(pulsar_dict))
print(pulsar_dict)