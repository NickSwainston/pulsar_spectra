import yaml
import psrqpy

with open("Zakharenko_2013_raw.txt", "r") as raw_file:
    lines = raw_file.readlines()
query = psrqpy.QueryATNF(params=['PSRJ', 'NAME', 'PSRB']).pandas

pulsar_dict = {}
for row in lines[:15]:
    row = row.replace(" ± ", "±").split(" ")
    print(row)
    bname = row[1].replace("−", "-")
    pid = list(query['PSRB']).index(bname)
    pulsar = query['PSRJ'][pid]

    pulsar_dict[pulsar] = {
        "Frequency MHz":[20, 25],
        "Bandwidth MHz":[4, 4],
        "Flux Density mJy":[float(row[2]), float(row[3])],
        "Flux Density error mJy":[float(row[7][1:]), float(row[8][1:])]
    }

for row in lines[16:]:
    row = row.replace(" ± ", "±").split(" ")
    print(row)
    if row[1].startswith("B"):
        bname = row[1].replace("−", "-")
        pid = list(query['PSRB']).index(bname)
        pulsar = query['PSRJ'][pid]
    else:
        pulsar = row[1].replace("−", "-")
    # Wrong names I found
    if pulsar == "J0927+23":
        pulsar = "J0927+2345"
    elif pulsar == "J1238+21":
        pulsar = "J1238+2152"

    flux, flux_err = row[2].split("±")
    pulsar_dict[pulsar] = {
        "Frequency MHz":[25],
        "Bandwidth MHz":[4],
        "Flux Density mJy":[float(flux)],
        "Flux Density error mJy":[float(flux_err)]
    }

with open("Zakharenko_2013.yaml", "w") as cat_file:
    yaml.safe_dump(pulsar_dict, cat_file, sort_keys=False, indent=2)