import json

with open("Bondonneau_2020_raw.txt", "r") as raw_file:
    lines = raw_file.readlines()
    print(lines)

pulsar_dict = {}
for row in lines[7:]:
    row = row.replace("()", "").replace("(τ)", "").split()
    print(row)
    pulsar = row[0].replace("–", "-").replace("−", "-")
    flux, flux_err = row[10].split("(")

    pulsar_dict[pulsar] = {"Frequency MHz":[float(row[8])], "Flux Density mJy":[float(flux)], "Flux Density error mJy":[float(flux_err[:-1])]}

with open("Bondonneau_2020.json", "w") as cat_file:
    cat_file.write(json.dumps(pulsar_dict))
print(pulsar_dict)