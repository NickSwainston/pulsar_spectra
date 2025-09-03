import yaml

with open("Dai_2015_raw.txt", "r") as raw_file:
    lines = raw_file.readlines()
    print(lines)

pulsar_dict = {}
for row in lines:
    row = row.replace(" ± ", "±").split(" ")
    print(row)
    pulsar = row[0].replace("−", "-")

    freqs = []
    bands = []
    fluxs = []
    flux_errs = []
    if len(row) == 9:
        flux, flux_err = row[1].split("±")
        freqs.append(730)
        bands.append(64)
        fluxs.append(float(flux))
        flux_errs.append(float(flux_err))

    flux, flux_err = row[-6].split("±")
    freqs.append(1400)
    bands.append(256)
    fluxs.append(float(flux))
    flux_errs.append(float(flux_err))

    flux, flux_err = row[-4].split("±")
    freqs.append(3100)
    bands.append(1024)
    fluxs.append(float(flux))
    flux_errs.append(float(flux_err))

    pulsar_dict[pulsar] = {
        "Frequency MHz":freqs,
        "Bandwidth MHz":bands,
        "Flux Density mJy":fluxs,
        "Flux Density error mJy":flux_errs
    }

with open("Dai_2015.yaml", "w") as cat_file:
    yaml.safe_dump(pulsar_dict, cat_file, sort_keys=False, indent=2)