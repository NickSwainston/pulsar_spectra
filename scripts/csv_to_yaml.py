#!/usr/bin/env python

import argparse
import json
import csv
import os


def convert_csv_to_yaml(csv_location, ref_label):
    pulsar_dict = {}

    # Read in the csv
    with open(csv_location, newline='') as csvfile:
        spamreader = csv.reader(csvfile)
        # This skips the header row of the CSV file.
        next(spamreader)
        print("Input data:")
        for row in spamreader:
            #logger.debug(row)
            print(row)
            pulsar, freq, flux, flux_err = row
            # Make sure there are no weird dash characters in the pulsar name
            pulsar = pulsar.replace("–", "-").replace("−", "-")
            if pulsar in pulsar_dict.keys():
                # Append the new data
                pulsar_dict[pulsar]["Frequency MHz"].append(float(freq))
                pulsar_dict[pulsar]["Flux Density mJy"].append(float(flux))
                pulsar_dict[pulsar]["Flux Density error mJy"].append(float(flux_err))
            else:
                # Make dict for this pulsar
                pulsar_dict[pulsar] = {"Frequency MHz":[float(freq)], "Flux Density mJy":[float(flux)], "Flux Density error mJy":[float(flux_err)]}

    # Dump the dict to the jsonfile in the catalogue directory
    with open(f"{os.path.dirname(os.path.realpath(__file__))}/../pulsar_spectra/catalogue_papers/{ref_label}.yaml", "w") as cat_file:
        cat_file.write(json.dumps(pulsar_dict))

    print("\nCatalogue data written:")
    print(json.dumps(pulsar_dict, indent=4))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Convert a csv file to pulsar_spectra catalogue formated yaml file.')
    parser.add_argument('--csv', type=str,
                        help='The location of the csv file')
    parser.add_argument('--ref', type=str,
                        help='The reference label (in the format "Author_year")')
    args = parser.parse_args()

    convert_csv_to_yaml(args.csv, args.ref)