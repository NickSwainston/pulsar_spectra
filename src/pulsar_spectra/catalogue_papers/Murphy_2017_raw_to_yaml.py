import yaml

pulsar_dict = {}

with open("Murphy_2017_raw_table_1_2.txt", "r") as raw_file:
    lines = raw_file.readlines()
    # print(lines)

for row in lines:
    row = row.replace(" ± ", "±").replace("(v) ", "").replace("–", "-").split()
    # print(row)
    print(row[0])
    pulsar = row[0].replace("−", "-")
    print(pulsar.replace("−", "-"))

    flux, flux_err = row[2].split("±")

    pulsar_dict[pulsar] = {
        "Frequency MHz": [151.5],
        "Bandwidth MHz": [159.0],
        "Flux Density mJy": [float(flux)],
        "Flux Density error mJy": [float(flux_err)],
    }

with open("Murphy_2017_raw_table_4.txt", "r") as raw_file:
    lines = raw_file.readlines()
    # print(lines)

for row in lines[:15]:
    row = (
        row.replace(" ± ", "±")
        .replace("(v) ", "")
        .replace(" 1 ", " 1")
        .replace(" 7 ", " 7")
        .replace(" 8 ", " 8")
        .replace(" 9 ", " 9")
        .replace(" 10 ", " 10")
        .split()
    )
    # print(row)
    pulsar = row[0].replace("−", "-")

    pulsar_dict[pulsar] = {
        "Frequency MHz": [],
        "Bandwidth MHz": [],
        "Flux Density mJy": [],
        "Flux Density error mJy": [],
    }

    for freq, pair in zip([76.0, 84.0, 92.0, 99.0, 107.0, 115.0, 122.0, 130.0, 143.0], row[3:], strict=False):
        if "<" not in pair:
            # print(pair)
            flux, flux_err = pair.split("±")
            pulsar_dict[pulsar]["Frequency MHz"] += [freq]
            pulsar_dict[pulsar]["Bandwidth MHz"] += [7.68]
            pulsar_dict[pulsar]["Flux Density mJy"] += [float(flux)]
            pulsar_dict[pulsar]["Flux Density error mJy"] += [float(flux_err)]
for row in lines[16:]:
    row = (
        row.replace(" ± ", "±")
        .replace("(v) ", "")
        .replace(" 1 ", " 1")
        .replace(" 2 ", " 2")
        .replace(" 3 ", " 3")
        .replace(" 4 ", " 4")
        .replace(" 5 ", " 5")
        .replace(" 6 ", " 6")
        .replace(" 7 ", " 7")
        .replace(" 8 ", " 8")
        .replace(" 9 ", " 9")
        .replace(" 10 ", " 10")
        .split()
    )
    # print(row)
    pulsar = row[0].replace("−", "-")

    for freq, pair in zip(
        [151.0, 158.0, 166.0, 174.0, 181.0, 189.0, 197.0, 204.5, 212.0, 220.0, 227.0], row[2:], strict=False
    ):
        if "<" not in pair:
            # print(pair)
            flux, flux_err = pair.split("±")
            pulsar_dict[pulsar]["Frequency MHz"] += [freq]
            pulsar_dict[pulsar]["Bandwidth MHz"] += [7.68]
            pulsar_dict[pulsar]["Flux Density mJy"] += [float(flux)]
            pulsar_dict[pulsar]["Flux Density error mJy"] += [float(flux_err)]

with open("Murphy_2017.yaml", "w") as cat_file:
    yaml.safe_dump(pulsar_dict, cat_file, sort_keys=False, indent=2)
