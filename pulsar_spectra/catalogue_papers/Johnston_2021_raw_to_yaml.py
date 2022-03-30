import json

with open("Johnston_2021_raw.txt", "r") as raw_file:
    lines = raw_file.readlines()
    print(lines)

pulsar_dict = {}
for row in lines[1:]:
    row = row.split()
    print(row)
    pulsar = row[0].replace("−", "-")
    flux = float(row[1])
    flux_err = float(row[2])
    pulsar_dict[pulsar] = {"Frequency MHz":[1400.], "Flux Density mJy":[flux], "Flux Density error mJy":[flux_err]}

with open("Johnston_2021.yaml", "w") as cat_file:
    cat_file.write(json.dumps(pulsar_dict))
print(pulsar_dict)