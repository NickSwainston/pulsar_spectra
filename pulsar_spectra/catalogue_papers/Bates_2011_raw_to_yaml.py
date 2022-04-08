import json

with open("Bates_2011_raw.txt", "r") as raw_file:
    lines = raw_file.readlines()

pulsar_dict = {}
for row in lines[:16]:
    row = row.split()
    print(row)
    pulsar = row[0].replace("−", "-")

    flux, flux_err = row[4].split("(")
    sig_fig = len(flux.split(".")[-1])
    pulsar_dict[pulsar] = {"Frequency MHz":[1400],
                           "Flux Density mJy":[float(flux)],
                           "Flux Density error mJy":[round(float(flux_err[:-1]) * 10**(-sig_fig), 4)]}

for row in lines[17:]:
    row = row.split()
    print(row)
    pulsar = row[0].replace("−", "-")

    freqs = [1400, 4850, 6500]
    pulsar_dict[pulsar] = {"Frequency MHz":[],
                           "Flux Density mJy":[],
                           "Flux Density error mJy":[]}
    for freq, pair in zip(freqs, row[6:-1]):
        print(freq,pair)
        if "(" in pair:
            flux, flux_err = pair.split("(")
            sig_fig = len(flux.split(".")[-1])
            pulsar_dict[pulsar]["Frequency MHz"] += [float(freq)]
            pulsar_dict[pulsar]["Flux Density mJy"] += [float(flux)]
            pulsar_dict[pulsar]["Flux Density error mJy"] += [round(float(flux_err[:-1]) * 10**(-sig_fig), 4)]

json = json.dumps(pulsar_dict)
with open("Bates_2011.yaml", "w") as cat_file:
    cat_file.write(json)
print(pulsar_dict)