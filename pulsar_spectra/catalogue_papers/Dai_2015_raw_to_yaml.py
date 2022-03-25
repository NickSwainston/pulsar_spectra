import json

with open("Dai_2015_raw.txt", "r") as raw_file:
    lines = raw_file.readlines()
    print(lines)

pulsar_dict = {}
for row in lines:
    row = row.replace(" ± ", "±").split(" ")
    print(row)
    pulsar = row[0].replace("−", "-")

    freqs = []
    fluxs = []
    flux_errs = []
    if len(row) == 9:
        flux, flux_err = row[1].split("±")
        freqs.append(730)
        fluxs.append(float(flux))
        flux_errs.append(float(flux_err))
    
    flux, flux_err = row[-6].split("±")
    freqs.append(1400)
    fluxs.append(float(flux))
    flux_errs.append(float(flux_err))

    flux, flux_err = row[-4].split("±")
    freqs.append(3100)
    fluxs.append(float(flux))
    flux_errs.append(float(flux_err))

    pulsar_dict[pulsar] = {"Frequency MHz":freqs,
                            "Flux Density mJy":fluxs,
                            "Flux Density error mJy":flux_errs}

json = json.dumps(pulsar_dict)
with open("Dai_2015.json", "w") as cat_file:
    cat_file.write(json)
print(pulsar_dict)