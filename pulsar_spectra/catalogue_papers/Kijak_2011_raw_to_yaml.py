import json
import psrqpy

with open("Kijak_2011_raw.txt", "r") as raw_file:
    lines = raw_file.readlines()
query = psrqpy.QueryATNF(params=['PSRJ', 'NAME', 'PSRB']).pandas

pulsar_dict = {}
for row in lines:
    row = row.split(",")
    print(row)
    if row[0].startswith("B"):
        bname = row[0].replace("−", "-")
        pid = list(query['PSRB']).index(bname)
        pulsar = query['PSRJ'][pid]
    else:
        pulsar = row[0].replace("−", "-")

    freqs = [610, 1170, 2640, 4850]
    pulsar_dict[pulsar] = {"Frequency MHz":[],
                           "Flux Density mJy":[],
                           "Flux Density error mJy":[]}
    for freq, pair in zip(freqs, row[1:]):
        if "±" in pair:
            flux, flux_err_pair = pair.split("±")
            flux_err, count = flux_err_pair.split("(")
            pulsar_dict[pulsar]["Frequency MHz"] += [float(freq)]
            pulsar_dict[pulsar]["Flux Density mJy"] += [float(flux)]
            pulsar_dict[pulsar]["Flux Density error mJy"] += [float(flux_err)]

json = json.dumps(pulsar_dict)
with open("Kijak_2011.json", "w") as cat_file:
    cat_file.write(json)
print(pulsar_dict)