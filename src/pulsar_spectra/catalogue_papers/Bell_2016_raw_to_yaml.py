import yaml

with open("Bell_2016_raw.txt", "r") as raw_file:
    lines = raw_file.readlines()
    print(lines)

pulsar_dict = {}
for row in lines[1:]:
    row = row.replace(" ± ", "±").split(" ")
    pulsar = row[1].replace("−", "-")
    flux, flux_err = row[7].split("±")
    pulsar_dict[pulsar] = {
        "Frequency MHz":[154.],
        "Bandwidth MHz":[30.72],
        "Flux Density mJy":[float(flux)*1e3],
        "Flux Density error mJy":[float(flux_err)*1e3]
    }

with open("Bell_2016.yaml", "w") as cat_file:
    yaml.safe_dump(pulsar_dict, cat_file, sort_keys=False, indent=2)