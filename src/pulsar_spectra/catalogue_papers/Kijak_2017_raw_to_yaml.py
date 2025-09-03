import yaml
import psrqpy

query = psrqpy.QueryATNF(params=['PSRJ', 'NAME', 'PSRB']).pandas

with open("Kijak_2017_raw.txt", "r") as raw_file:
    lines = raw_file.readlines()
    print(lines)

pulsar_dict = {}
for row in lines[:9]:
    row = row.replace("±", "±").split(" ")
    print(row)
    if row[0].startswith("B"):
        bname = row[0].replace("−", "-")
        pid = list(query['PSRB']).index(bname)
        pulsar = query['PSRJ'][pid]
    else:
        pulsar = row[0].replace("−", "-")

    if "±" in row[2]:
        flux, flux_err = row[2].split("±")
        pulsar_dict[pulsar] = {
            "Frequency MHz":[325],
            "Bandwidth MHz":[33],
            "Flux Density mJy":[float(flux)],
            "Flux Density error mJy":[float(flux_err)]
        }
for row in lines[10:]:
    row = row.replace("±", "±").split(" ")
    print(row)
    if row[0].startswith("B"):
        bname = row[0].replace("−", "-")
        pid = list(query['PSRB']).index(bname)
        pulsar = query['PSRJ'][pid]
    else:
        pulsar = row[0].replace("−", "-")

    if "±" in row[2]:
        flux, flux_err = row[2].split("±")
        pulsar_dict[pulsar] = {
            "Frequency MHz":[610],
            "Bandwidth MHz":[33],
            "Flux Density mJy":[float(flux)],
            "Flux Density error mJy":[float(flux_err)]
        }

with open("Kijak_2017.yaml", "w") as cat_file:
    yaml.safe_dump(pulsar_dict, cat_file, sort_keys=False, indent=2)