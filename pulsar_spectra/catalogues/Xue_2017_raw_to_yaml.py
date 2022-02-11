import json

with open("Xue_2017_raw.txt", "r") as raw_file:
    lines = raw_file.readlines()
    print(lines)

pulsar_dict = {}
for row in lines[7:]:
    row = row.replace(" ± ", "±").split()
    print(row)
    print(len(row))
    pulsar = row[0].replace("–", "-").replace("+", "+")
    print(row[7])
    if '†' in row[7]:
        freqs = []
        fluxs = []
        flux_errs = []
    else:
        freqs     = [185.]
        fluxs     = [float(row[7].split("±")[0])]
        flux_errs = [float(row[7].split("±")[1])]

    if "±" in row[8]:
        freqs.append(200.)
        fluxs.append(float(row[8].split("±")[0]))
        flux_errs.append(float(row[8].split("±")[1]))
    print(freqs)
    print(fluxs)
    print(flux_errs)


    pulsar_dict[pulsar] = {"Frequency MHz":freqs, "Flux Density mJy":fluxs, "Flux Density error mJy":flux_errs}

with open("Xue_2017.json", "w") as cat_file:
    cat_file.write(json.dumps(pulsar_dict))
print(pulsar_dict)