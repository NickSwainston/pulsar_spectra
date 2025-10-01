#!/usr/bin/env python

import argparse
import csv

import psrqpy
import yaml

from pulsar_spectra.catalogue import ATNF_VER

query = psrqpy.QueryATNF(version=ATNF_VER, params=["PSRJ", "NAME", "PSRB"]).pandas
all_jnames = list(query["PSRJ"])


class ListIndentDumper(yaml.Dumper):
    # Will indent lists properly for more readable yaml files
    def increase_indent(self, flow=False, indentless=False):
        return super(ListIndentDumper, self).increase_indent(flow, False)


def dump_yaml(pulsar_dict, filename):
    with open(filename, "w") as cat_file:
        yaml.dump(pulsar_dict, cat_file, sort_keys=False, indent=2, default_flow_style=False, Dumper=ListIndentDumper)


def convert_csv_to_yaml(csv_location, ref_label, obs_span, data_type):
    pulsar_dict = {
        "Paper Metadata": {
            "Data Type": data_type,
            "Observation Span": obs_span,
        }
    }

    # Read in the csv
    with open(csv_location, newline="") as csvfile:
        spamreader = csv.reader(csvfile)
        # This skips the header row of the CSV file.
        next(spamreader)
        print("Input data:")
        for row in spamreader:
            # logger.debug(row)
            # print(row)
            if len(row) == 5:
                pulsar, freq, band, flux, flux_err = row
            elif len(row) == 4:
                pulsar, freq, band, flux = row
                flux_err = float(flux) * 0.5
            else:
                print(f"Error on row: {row}")
                continue
            # Make sure there are no weird dash characters in the pulsar name
            pulsar = pulsar.replace("–", "-").replace("−", "-")
            if pulsar.startswith("B"):
                # convert from Bname to Jname
                pid = list(query["PSRB"]).index(pulsar)
                pulsar = query["PSRJ"][pid]
            if pulsar not in all_jnames:
                print(f"{pulsar} not in the ANTF")

            if pulsar in pulsar_dict.keys():
                # Append the new data
                pulsar_dict[pulsar]["Frequency MHz"].append(float(freq))
                pulsar_dict[pulsar]["Bandwidth MHz"].append(float(band))
                pulsar_dict[pulsar]["Flux Density mJy"].append(float(flux))
                pulsar_dict[pulsar]["Flux Density error mJy"].append(float(flux_err))
            else:
                # Make dict for this pulsar
                pulsar_dict[pulsar] = {
                    "Frequency MHz": [float(freq)],
                    "Bandwidth MHz": [float(band)],
                    "Flux Density mJy": [float(flux)],
                    "Flux Density error mJy": [float(flux_err)],
                }

    # Dump the dict to the yaml file in the catalogue directory
    dump_yaml(pulsar_dict, f"{ref_label}.yaml")

    print("\nCatalogue data written:")
    print(yaml.dump(pulsar_dict, sort_keys=False, indent=2))


def main():
    parser = argparse.ArgumentParser(description="Convert a csv file to pulsar_spectra catalogue formated yaml file.")
    parser.add_argument("--csv", type=str, help="The location of the csv file")
    parser.add_argument("--ref", type=str, help='The reference label (in the format "Author_year")')
    parser.add_argument("--obs_span", type=str, help='The observation span ("Single-epoch", "Multi-epoch" or "Long-term")', default="Single-epoch", choices=["Single-epoch", "Multi-epoch", "Long-term"])
    parser.add_argument("--data_type", type=str, help='The data type ("Beamforming" or "Imaging")', default="Beamforming", choices=["Beamforming", "Imaging"])
    args = parser.parse_args()

    convert_csv_to_yaml(args.csv, args.ref, args.obs_span, args.data_type)


if __name__ == "__main__":
    main()
