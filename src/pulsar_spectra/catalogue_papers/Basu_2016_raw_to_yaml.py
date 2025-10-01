import yaml

from pulsar_spectra.scripts.csv_to_yaml import dump_yaml

with open("Basu_2016_raw.txt", "r") as raw_file:
    lines = raw_file.readlines()
    print(lines)

pulsar = "J1803-2137"
pulsar_dict = {
    "Paper Metadata": {
        "Data Type": "Beamforming",
        "Observation Span": "Single-epoch",
    },
    pulsar: {
        "Frequency MHz": [],
        "Bandwidth MHz": [],
        "Flux Density mJy": [],
        "Flux Density error mJy": []
    }
}
for row in lines:
    row = row.replace(" ± ", "±").split(" ")
    print(row)
    freq = float(row[-3])
    flux1, flux_err1 = row[-2].split("±")
    pulsar_dict[pulsar]["Frequency MHz"] += [freq]
    pulsar_dict[pulsar]["Bandwidth MHz"] += [33]
    pulsar_dict[pulsar]["Flux Density mJy"] += [float(flux1)]
    pulsar_dict[pulsar]["Flux Density error mJy"] += [float(flux_err1)]
    if "±" in row[-1]:
        flux2, flux_err2 = row[-1].split("±")
        pulsar_dict[pulsar]["Frequency MHz"] += [freq]
        pulsar_dict[pulsar]["Bandwidth MHz"] += [33]
        pulsar_dict[pulsar]["Flux Density mJy"] += [float(flux2)]
        pulsar_dict[pulsar]["Flux Density error mJy"] += [float(flux_err2)]

class ListIndentDumper(yaml.Dumper):
    # Will indent lists properly for more readable yaml files
    def increase_indent(self, flow=False, indentless=False):
        return super(ListIndentDumper, self).increase_indent(flow, False)

dump_yaml(pulsar_dict, "Basu_2016.yaml")