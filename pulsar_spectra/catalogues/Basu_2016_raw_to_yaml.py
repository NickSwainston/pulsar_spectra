import json

with open("Basu_2016_raw.txt", "r") as raw_file:
    lines = raw_file.readlines()
    print(lines)

pulsar = "J1803-2137"
pulsar_dict = {pulsar: {"Frequency MHz":[],
                        "Flux Density mJy":[],
                        "Flux Density error mJy":[]}}
for row in lines:
    row = row.replace(" ± ", "±").split(" ")
    print(row)
    freq = float(row[-3])
    flux1, flux_err1 = row[-2].split("±")
    pulsar_dict[pulsar]["Frequency MHz"] += [freq]
    pulsar_dict[pulsar]["Flux Density mJy"] += [float(flux1)]
    pulsar_dict[pulsar]["Flux Density error mJy"] += [float(flux_err1)]
    if "±" in row[-1]:
        flux2, flux_err2 = row[-1].split("±")
        pulsar_dict[pulsar]["Frequency MHz"] += [freq]
        pulsar_dict[pulsar]["Flux Density mJy"] += [float(flux2)]
        pulsar_dict[pulsar]["Flux Density error mJy"] += [float(flux_err2)]
json = json.dumps(pulsar_dict)
with open("Basu_2016.json", "w") as cat_file:
    cat_file.write(json)
print(pulsar_dict)