import yaml
import csv
import psrqpy

query = psrqpy.QueryATNF(params=['PSRJ', 'NAME', 'PSRB']).pandas
all_jnames = list(query['PSRJ'])

with open("Hobbs_2004a_raw_table_1-4.tsv") as file:
    tsv_file = csv.reader(file, delimiter="\t")
    lines = []
    for line in tsv_file:
        lines.append(line)
print(lines)

pulsar_dict = {}
for row in lines:
    row = [r.strip() for r in row]
    if len(row) == 0:
        continue
    if row[0].startswith("#") or row[0].startswith("PSR") or row[0] == '' or row[0].startswith('-'):
        continue
    #print(row)

    pulsar = "J" + row[0].strip().replace("–", "-")
    if pulsar == "J1915+07":
        pulsar = "J1915+0752"
    if pulsar not in all_jnames:
        print(pulsar)

    pulsar_dict[pulsar] = {
        "Frequency MHz":[1400],
        "Bandwidth MHz":[100],
        "Flux Density mJy":[float(row[1])],
        "Flux Density error mJy":[float(row[2])]
    }

with open("Hobbs_2004a_raw_table_7.tsv") as file:
    tsv_file = csv.reader(file, delimiter="\t")
    lines = []
    for line in tsv_file:
        lines.append(line)
#print(lines)

for row in lines:
    row = [r.strip() for r in row]
    if len(row) < 2:
        continue
    if row[0].startswith("#") or row[0].startswith("PSR") or row[0] == '' or row[0].startswith('-'):
        continue
    if row[1] == '':
        continue
    #print(row)

    pulsar = row[0].strip().replace("–", "-")
    # Wrong names I found
    if pulsar == "J0820-3927":
        pulsar = "J0820-3921"
    elif pulsar == "J1356-6230":
        pulsar = "J1357-62"
    elif pulsar == "J1537-49":
        pulsar = "J1537-4912"
    elif pulsar == "J1748-2021":
        pulsar = "J1748-2021A"
    elif pulsar == "J1748-2446":
        pulsar = "J1748-2446A"
    elif pulsar == "J1807-2459":
        pulsar = "J1807-2459A"
    elif pulsar == "J1824-2452":
        pulsar = "J1824-2452A"
    elif pulsar == "J1849+06":
        pulsar = "J1848+0604"
    elif pulsar == "J1915+07":
        pulsar = "J1915+0752"
    elif pulsar == "J1916+07":
        pulsar = "J1916+0748"
    elif pulsar == "J1918+08":
        pulsar = "J1917+0834"

    if pulsar not in all_jnames:
        print(pulsar)

    if pulsar in pulsar_dict.keys():
        print("no key",pulsar)
        exit()
    pulsar_dict[pulsar] = {
        "Frequency MHz":[1400],
        "Bandwidth MHz":[100],
        "Flux Density mJy":[float(row[1])],
        "Flux Density error mJy":[float(row[2])]
    }


with open("Hobbs_2004a.yaml", "w") as cat_file:
    yaml.safe_dump(pulsar_dict, cat_file, sort_keys=False, indent=2)