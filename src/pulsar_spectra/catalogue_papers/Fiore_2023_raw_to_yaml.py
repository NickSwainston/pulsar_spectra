import yaml
import psrqpy
import csv

from pulsar_spectra.scripts.csv_to_yaml import dump_yaml

query = psrqpy.QueryATNF(params=['PSRJ', 'NAME', 'PSRB', 'P0']).pandas
all_jnames = list(query['PSRJ'])

pulsar_dict = {
    "Paper Metadata": {
        "Data Type": "Beamforming",
        "Observation Span": "Single-epoch",
    }
}

with open("Fiore_2023_raw.txt") as file:
    tsv_file = csv.reader(file, delimiter=" ")
    lines = []
    for line in tsv_file:
        lines.append(line)

for row in lines:
    if row[0].startswith("#") or row[0].strip() == "":
        continue
    row = [r.strip() for r in row]
    print(row)

    pulsar = row[0].strip().replace("–", "-").replace(" ", "").replace("−", "-")

    if pulsar not in all_jnames:
        print(pulsar)

    pulsar_dict[pulsar] = {
        "Frequency MHz":[],
        "Bandwidth MHz":[],
        "Flux Density mJy":[],
        "Flux Density error mJy":[]
    }

    flux, flux_err = row[2].split("(")
    if "." in flux:
        sig_fig = len(flux.split(".")[-1])
    else:
        sig_fig = 0
    flux = float(flux)
    flux_err = round(float(flux_err[:-1]) * 10**(-sig_fig), sig_fig)
    pulsar_dict[pulsar]["Frequency MHz"].append(350.0)
    pulsar_dict[pulsar]["Bandwidth MHz"].append(100.0)
    if pulsar == "J2104+2830":
        # Round to 1 decimal place for this pulsar to align with ATNF
        pulsar_dict[pulsar]["Flux Density mJy"].append(round(flux, 1))
    else:
        pulsar_dict[pulsar]["Flux Density mJy"].append(flux)
    pulsar_dict[pulsar]["Flux Density error mJy"].append(flux_err)

    if "L" not in row[4]:
        flux, flux_err = row[4].split("(")
        if "." in flux:
            sig_fig = len(flux.split(".")[-1])
        else:
            sig_fig = 0
        flux = float(flux)
        flux_err = round(float(flux_err[:-1]) * 10**(-sig_fig), sig_fig)
        pulsar_dict[pulsar]["Frequency MHz"].append(430.0)
        pulsar_dict[pulsar]["Bandwidth MHz"].append(100.0)
        pulsar_dict[pulsar]["Flux Density mJy"].append(flux)
        pulsar_dict[pulsar]["Flux Density error mJy"].append(flux_err)

    flux, flux_err = row[6].split("(")
    if "." in flux:
        sig_fig = len(flux.split(".")[-1])
    else:
        sig_fig = 0
    flux = float(flux)
    flux_err = round(float(flux_err[:-1]) * 10**(-sig_fig), sig_fig)
    pulsar_dict[pulsar]["Frequency MHz"].append(820.0)
    pulsar_dict[pulsar]["Bandwidth MHz"].append(100.0)
    pulsar_dict[pulsar]["Flux Density mJy"].append(flux)
    pulsar_dict[pulsar]["Flux Density error mJy"].append(flux_err)

    if "L" not in row[8]:
        flux, flux_err = row[8].split("(")
        if "." in flux:
            sig_fig = len(flux.split(".")[-1])
        else:
            sig_fig = 0
        flux = float(flux)
        flux_err = round(float(flux_err[:-1]) * 10**(-sig_fig), sig_fig)
        pulsar_dict[pulsar]["Frequency MHz"].append(1380.0)
        pulsar_dict[pulsar]["Bandwidth MHz"].append(100.0)
        pulsar_dict[pulsar]["Flux Density mJy"].append(flux)
        pulsar_dict[pulsar]["Flux Density error mJy"].append(flux_err)

    if "L" not in row[10]:
        flux, flux_err = row[10].split("(")
        if "." in flux:
            sig_fig = len(flux.split(".")[-1])
        else:
            sig_fig = 0
        flux = float(flux)
        flux_err = round(float(flux_err[:-1]) * 10**(-sig_fig), sig_fig)
        pulsar_dict[pulsar]["Frequency MHz"].append(2000.0)
        pulsar_dict[pulsar]["Bandwidth MHz"].append(100.0)
        pulsar_dict[pulsar]["Flux Density mJy"].append(flux)
        pulsar_dict[pulsar]["Flux Density error mJy"].append(flux_err)

# Add extra J1327+3423 values
pulsar = "J1327+3423"

pulsar_dict[pulsar]["Frequency MHz"].append(35.1)
pulsar_dict[pulsar]["Bandwidth MHz"].append(16)
pulsar_dict[pulsar]["Flux Density mJy"].append(80)
pulsar_dict[pulsar]["Flux Density error mJy"].append(50)

pulsar_dict[pulsar]["Frequency MHz"].append(49.8)
pulsar_dict[pulsar]["Bandwidth MHz"].append(16)
pulsar_dict[pulsar]["Flux Density mJy"].append(210)
pulsar_dict[pulsar]["Flux Density error mJy"].append(130)

pulsar_dict[pulsar]["Frequency MHz"].append(64.5)
pulsar_dict[pulsar]["Bandwidth MHz"].append(16)
pulsar_dict[pulsar]["Flux Density mJy"].append(200)
pulsar_dict[pulsar]["Flux Density error mJy"].append(130)

pulsar_dict[pulsar]["Frequency MHz"].append(79.2)
pulsar_dict[pulsar]["Bandwidth MHz"].append(16)
pulsar_dict[pulsar]["Flux Density mJy"].append(180)
pulsar_dict[pulsar]["Flux Density error mJy"].append(110)

dump_yaml(pulsar_dict, "Fiore_2023.yaml")