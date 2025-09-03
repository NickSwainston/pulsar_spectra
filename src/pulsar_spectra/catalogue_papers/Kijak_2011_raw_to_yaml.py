import yaml
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
    bands = [16, 16, 100, 500]
    pulsar_dict[pulsar] = {
        "Frequency MHz":[],
        "Bandwidth MHz":[],
        "Flux Density mJy":[],
        "Flux Density error mJy":[]
    }
    for freq, band, pair in zip(freqs, bands, row[1:]):
        if "±" in pair:
            flux, flux_err_pair = pair.split("±")
            flux_err, count = flux_err_pair.split("(")
            pulsar_dict[pulsar]["Frequency MHz"] += [float(freq)]
            pulsar_dict[pulsar]["Bandwidth MHz"] += [float(band)]
            pulsar_dict[pulsar]["Flux Density mJy"] += [float(flux)]
            pulsar_dict[pulsar]["Flux Density error mJy"] += [float(flux_err)]

with open("Kijak_2011.yaml", "w") as cat_file:
    yaml.safe_dump(pulsar_dict, cat_file, sort_keys=False, indent=2)