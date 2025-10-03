import yaml
import psrqpy

from pulsar_spectra.scripts.csv_to_yaml import dump_yaml

with open("Stovall_2015_raw.txt", "r") as raw_file:
    lines = raw_file.readlines()
    print(lines)

query = psrqpy.QueryATNF(params=['PSRJ', 'NAME', 'PSRB']).pandas

pulsar_dict = {
    "Paper Metadata": {
        "Data Type": "Beamforming",
        "Observation Span": "Single-epoch",
    }
}
for row in lines:
    row = row.replace("()", "").replace("(τ)", "").split()
    print(row)
    bname = row[0].replace("–", "-")
    print(query['PSRB'])
    pid = list(query['PSRB']).index(bname)
    pulsar = query['PSRJ'][pid]
    flux, flux_err = row[7].split("(")

    if pulsar in pulsar_dict.keys():
        pulsar_dict[pulsar]["Frequency MHz"] += [float(row[1])]
        pulsar_dict[pulsar]["Bandwidth MHz"] += [19.6]
        pulsar_dict[pulsar]["Flux Density mJy"] += [float(flux)]
        pulsar_dict[pulsar]["Flux Density error mJy"] += [float(flux_err[:-1])]
    else:
        pulsar_dict[pulsar] = {
            "Frequency MHz":[float(row[1])],
            "Bandwidth MHz":[19.6],
            "Flux Density mJy":[float(flux)],
            "Flux Density error mJy":[float(flux_err[:-1])]
        }

dump_yaml(pulsar_dict, "Stovall_2015.yaml")