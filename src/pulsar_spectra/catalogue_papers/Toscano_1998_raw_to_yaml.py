import yaml
import psrqpy
import csv

query = psrqpy.QueryATNF(params=['PSRJ', 'NAME', 'PSRB', 'P0']).pandas
all_jnames = list(query['PSRJ'])

# was converted from image to csv using ABBYY FineReader
with open("Toscano_1998_raw.csv") as file:
    tsv_file = csv.reader(file, delimiter=" ")
    lines = []
    for line in tsv_file:
        lines.append(line)

pulsar_dict = {}
for row in lines:
    row = [r.strip() for r in row]

    pulsar = "J" + row[0].strip().replace("–", "-").replace(" ", "").replace("−", "-")

    # Incorrect names
    if pulsar == "J1804-2718":
        pulsar = "J1804-2717"
    if pulsar == "J2129-5718":
        pulsar = "J2129-5721"
    if pulsar not in all_jnames:
        print(pulsar)

    pulsar_dict[pulsar] = {
        "Frequency MHz":[],
        "Bandwidth MHz":[],
        "Flux Density mJy":[],
        "Flux Density error mJy":[]
    }

    freq_band_row = [
        (436, 32, 1),
        (660, 32, 2),
        (1400, 128, 3),
        (1660, 128, 4)
    ]
    for freq, band, row_id in freq_band_row:
        if "..." in row[row_id]:
            continue
        flux, flux_err = row[row_id].split("(")
        if "." in flux:
            sig_fig = len(flux.split(".")[-1])
        else:
            sig_fig = 0
        flux = float(flux)
        flux_err = round(float(flux_err[:-1]) * 10**(-sig_fig), sig_fig)
        pulsar_dict[pulsar]["Frequency MHz"].append(freq)
        pulsar_dict[pulsar]["Bandwidth MHz"].append(band)
        pulsar_dict[pulsar]["Flux Density mJy"].append(flux)
        pulsar_dict[pulsar]["Flux Density error mJy"].append(flux_err)

with open("Toscano_1998.yaml", "w") as cat_file:
    yaml.safe_dump(pulsar_dict, cat_file, sort_keys=False, indent=2)