import json

pulsar_dict = {}

with open("Murphy_2017_raw_table_1_2.txt", "r") as raw_file:
    lines = raw_file.readlines()
    #print(lines)

for row in lines:
    row = row.replace(" ± ", "±").replace("(v) ", "").replace("–", "-").split()
    #print(row)
    print(row[0])
    pulsar = row[0].replace("−", "-")
    print(pulsar.replace("−", "-"))

    flux, flux_err = row[2].split("±")

    pulsar_dict[pulsar] = {
        "Frequency MHz":[151.5],
        "Bandwidth MHz":[159],
        "Flux Density mJy":[float(flux)],
        "Flux Density error mJy":[float(flux_err)]
    }

with open("Murphy_2017_raw_table_4.txt", "r") as raw_file:
    lines = raw_file.readlines()
    #print(lines)

for row in lines[:15]:
    row = row.replace(" ± ", "±").replace("(v) ", "").\
              replace(" 1 ", " 1").replace(" 7 ", " 7").replace(" 8 ", " 8").replace(" 9 ", " 9").replace(" 10 ", " 10").split()
    #print(row)
    pulsar = row[0].replace("−", "-")

    for freq, pair in zip([76, 84, 92, 99, 107, 115, 122, 130, 143], row[3:]):
        if "<" not in pair:
            #print(pair)
            flux, flux_err = pair.split("±")
            pulsar_dict[pulsar]["Frequency MHz"] += [freq]
            pulsar_dict[pulsar]["Bandwidth MHz"] += [7.68]
            pulsar_dict[pulsar]["Flux Density mJy"] +=[float(flux)]
            pulsar_dict[pulsar]["Flux Density error mJy"] += [float(flux_err)]
for row in lines[16:]:
    row = row.replace(" ± ", "±").replace("(v) ", "").\
              replace(" 1 ", " 1").replace(" 2 ", " 2").replace(" 3 ", " 3").replace(" 4 ", " 4").replace(" 5 ", " 5").\
              replace(" 6 ", " 6").replace(" 7 ", " 7").replace(" 8 ", " 8").replace(" 9 ", " 9").replace(" 10 ", " 10").split()
    #print(row)
    pulsar = row[0].replace("−", "-")

    for freq, pair in zip([151, 158, 166, 174, 181, 189, 197, 204.5, 212, 220, 227], row[2:]):
        if "<" not in pair:
            #print(pair)
            flux, flux_err = pair.split("±")
            pulsar_dict[pulsar]["Frequency MHz"] += [freq]
            pulsar_dict[pulsar]["Bandwidth MHz"] += [7.68]
            pulsar_dict[pulsar]["Flux Density mJy"] +=[float(flux)]
            pulsar_dict[pulsar]["Flux Density error mJy"] += [float(flux_err)]

with open("Murphy_2017.yaml", "w") as cat_file:
    cat_file.write(json.dumps(pulsar_dict, indent=1))
print(pulsar_dict)