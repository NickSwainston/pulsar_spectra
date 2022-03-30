import json

with open("Kijak_2017_raw.txt", "r") as raw_file:
    lines = raw_file.readlines()
    print(lines)

pulsar_dict = {}
for row in lines[:9]:
    row = row.replace("±", "±").split(" ")
    print(row)
    pulsar = row[0].replace("−", "-")
    if "±" in row[2]:
        flux, flux_err = row[2].split("±")
        pulsar_dict[pulsar] = {"Frequency MHz":[325],
                               "Flux Density mJy":[float(flux)],
                               "Flux Density error mJy":[float(flux_err)]}
for row in lines[10:]:
    row = row.replace("±", "±").split(" ")
    print(row)
    pulsar = row[0].replace("−", "-")
    if "±" in row[2]:
        flux, flux_err = row[2].split("±")
        pulsar_dict[pulsar] = {"Frequency MHz":[610],
                               "Flux Density mJy":[float(flux)],
                               "Flux Density error mJy":[float(flux_err)]}

json = json.dumps(pulsar_dict)
with open("Kijak_2017.yaml", "w") as cat_file:
    cat_file.write(json)
print(pulsar_dict)