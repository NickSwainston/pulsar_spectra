import yaml
import csv

with open("Zhang_2019_raw.csv") as file:
    tsv_file = csv.reader(file, delimiter=" ")
    lines = []
    for line in tsv_file:
        lines.append(line)


pulsar_dict = {}
pulsar_dict["J0024-7204C"] = {
    "Frequency MHz":[],
    "Bandwidth MHz":[],
    "Flux Density mJy":[],
    "Flux Density error mJy":[]
}
pulsar_dict["J0024-7204D"] = {
    "Frequency MHz":[],
    "Bandwidth MHz":[],
    "Flux Density mJy":[],
    "Flux Density error mJy":[]
}
pulsar_dict["J0024-7204J"] = {
    "Frequency MHz":[],
    "Bandwidth MHz":[],
    "Flux Density mJy":[],
    "Flux Density error mJy":[]
}

pulsars = [
    ("J0024-7204C", 1),
    ("J0024-7204D", 2),
    ("J0024-7204J", 3),
]

for row in lines:
    row = [r.strip() for r in row]

    for pulsar, row_id in pulsars:
        freq = float(row[0][1:])
        flux, flux_err = row[row_id].split("(")
        sig_fig = len(flux.split(".")[-1])
        flux = float(flux)
        flux_err = round(float(flux_err[:-1]) * 10**(-sig_fig), sig_fig)
        pulsar_dict[pulsar]["Frequency MHz"] += [freq]
        pulsar_dict[pulsar]["Bandwidth MHz"] += [128]
        pulsar_dict[pulsar]["Flux Density mJy"] += [flux]
        pulsar_dict[pulsar]["Flux Density error mJy"] += [flux_err]

with open("Zhang_2019.yaml", "w") as cat_file:
    yaml.safe_dump(pulsar_dict, cat_file, sort_keys=False, indent=2)