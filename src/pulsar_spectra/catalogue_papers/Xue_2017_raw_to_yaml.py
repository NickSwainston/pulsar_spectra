import yaml

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
    if '†' not in row[7]:
        freqs     = [185.]
        bands     = [30.72]
        fluxs     = [float(row[7].split("±")[0])]
        flux_errs = [float(row[7].split("±")[1])]

        print(freqs)
        print(fluxs)
        print(flux_errs)

        pulsar_dict[pulsar] = {
            "Frequency MHz":freqs,
            "Bandwidth MHz":bands,
            "Flux Density mJy":fluxs,
            "Flux Density error mJy":flux_errs
        }

with open("Xue_2017.yaml", "w") as cat_file:
    yaml.safe_dump(pulsar_dict, cat_file, sort_keys=False, indent=2)