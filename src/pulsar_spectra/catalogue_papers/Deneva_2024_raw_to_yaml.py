import yaml
import psrqpy

query = psrqpy.QueryATNF(params=["PSRJ", "NAME", "PSRB", "P0"]).pandas
all_jnames = list(query["PSRJ"])

with open("Deneva_2024_raw.csv", "r") as raw_file:
    lines = raw_file.readlines()
    print(lines)

pulsar_dict = {}
for row in lines:
    if row.startswith("#") or row.strip() == "":
        continue
    row = row.split("|")
    print(row)
    pulsar = row[0].strip().replace("−", "-")

    if pulsar.startswith("B"):
        print(f"Found B name {pulsar}")
        pid = list(query["PSRB"]).index(pulsar)
        pulsar = query["PSRJ"][pid]
        print(f"Converted to J name {pulsar}")

    # Wrong names I've found
    if pulsar == "J2017+2819g":
        pulsar = "J2017+2819"
    elif pulsar == "J2023+2853g":
        pulsar = "J2023+2853_P"

    pulsar_dict[pulsar] = {
        "Frequency MHz": [327.0],
        "Bandwidth MHz": [68.75],
        "Flux Density mJy": [float(row[2].strip())],
        "Flux Density error mJy": [float(row[3].strip())]
    }

with open("Deneva_2024.yaml", "w") as cat_file:
    yaml.safe_dump(pulsar_dict, cat_file, sort_keys=False, indent=2)