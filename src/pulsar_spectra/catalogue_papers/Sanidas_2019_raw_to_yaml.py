import yaml
import csv
import psrqpy

with open("Sanidas_2019_raw.tsv") as file:
    tsv_file = csv.reader(file, delimiter="\t")
    lines = []
    for line in tsv_file:
        lines.append(line)
print(lines)

query = psrqpy.QueryATNF(params=['PSRJ', 'NAME', 'PSRB']).pandas
all_jnames = list(query['PSRJ'])
#print(query['PSRB'])

pulsar_dict = {}
for row in lines:
    row = [r.strip() for r in row]
    if len(row) == 0:
        continue
    if row[0].startswith("#") or row[0].startswith("PSR") or row[0] == '' or row[0].startswith('-'):
        continue
    #print(row)

    if row[0].startswith("B"):
        bname = row[0].strip().replace("–", "-")
        pid = list(query['PSRB']).index(bname)
        pulsar = query['PSRJ'][pid]
    else:
        pulsar = row[0].strip().replace("–", "-")
    # Wrong names I found
    if pulsar == "J0201+7002":
        pulsar = "J0201+7005"
    elif pulsar == "J0338+66":
        pulsar = "J0335+6623"
    elif pulsar == "J0358+42":
        pulsar = "J0358+4155"
    elif pulsar == "J0358+66":
        pulsar = "J0358+6627"
    elif pulsar == "J0435+27":
        pulsar = "J0435+2749"
    elif pulsar == "J0517+22":
        pulsar = "J0517+2212"
    elif pulsar == "J0519+54":
        pulsar = "J0518+5416"
    elif pulsar == "J0608+16":
        pulsar = "J0608+1635"
    elif pulsar == "J0610+37":
        pulsar = "J0612+37216"
    elif pulsar == "J0943+22":
        pulsar = "J0943+2253"
    elif pulsar == "J0943+41":
        pulsar = "J0944+4106"
    elif pulsar == "J0947+27":
        pulsar = "J0947+2740"
    elif pulsar == "J1101+65":
        pulsar = "J1059+6459"
    elif pulsar == "J1134+24":
        pulsar = "J1132+25"
    elif pulsar == "J1246+22":
        pulsar = "J1246+2253"
    elif pulsar == "J1327+34":
        pulsar = "J1326+33"
    elif pulsar == "J1411+25":
        pulsar = "J1411+2551"
    elif pulsar == "J1647+66":
        pulsar = "J1647+6608"
    elif pulsar == "J1800+50":
        pulsar = "J1800+5034"
    elif pulsar == "J1806+28":
        pulsar = "J1806+2819"
    elif pulsar == "J1815+55":
        pulsar = "J1815+5546"
    elif pulsar == "J1821+41":
        pulsar = "J1821+4147"
    elif pulsar == "J1844+21":
        pulsar = "J1843+2024"
    elif pulsar == "J1921+42":
        pulsar = "J1923+4243"
    elif pulsar == "J1930-01":
        pulsar = "J1931-0144"
    elif pulsar == "J1935+52":
        pulsar = "J1934+5219"
    elif pulsar == "J1941+43":
        pulsar = "J1941+4320"
    elif pulsar == "J1942+81":
        pulsar = "J1942+8106"
    elif pulsar == "J1952+30":
        pulsar = "J1952+3021"
    elif pulsar == "J1954+43":
        pulsar = "J1954+4357"
    elif pulsar == "J2000+29":
        pulsar = "J2000+2920"
    elif pulsar == "J2001+42":
        pulsar = "J2001+4258"
    elif pulsar == "J2017+59":
        pulsar = "J2017+5906"
    elif pulsar == "J2027+74":
        pulsar = "J2027+7502"
    elif pulsar == "J2137+64":
        pulsar = "J2137+6428"
    elif pulsar == "J2207+40":
        pulsar = "J2208+4056"
    elif pulsar == "J2243+69":
        pulsar = "J2241+6941"
    elif pulsar == "J2316+69":
        pulsar = "J2312+6931"
    elif pulsar == "J2353+85":
        pulsar = "J2351+8533"
    elif pulsar == "J2356+22":
        pulsar = "J2355+2246"
    elif pulsar == "J2227+30":
        pulsar = "J2227+3038"
    elif pulsar == "J0220+36":
        pulsar = "J0220+3626"
    elif pulsar == "J1629+43":
        pulsar = "J1628+4406"

    # CAN'T FIND THIS IN ATNF
    if pulsar == "J2301+48":
        continue
    elif pulsar == "J2228+40":
        continue

    if pulsar not in all_jnames:
        print(pulsar)


    pulsar_dict[pulsar] = {
        "Frequency MHz":[],
        "Bandwidth MHz":[],
        "Flux Density mJy":[],
        "Flux Density error mJy":[]
    }

    if row[1] != '':
        pulsar_dict[pulsar]["Frequency MHz"] += [135.25]
        pulsar_dict[pulsar]["Bandwidth MHz"] += [31.64]
        pulsar_dict[pulsar]["Flux Density mJy"] += [float(row[1])]
        pulsar_dict[pulsar]["Flux Density error mJy"] += [float(row[1])*0.5]
    if len(pulsar_dict[pulsar]["Frequency MHz"]) == 0:
        del pulsar_dict[pulsar]

with open("Sanidas_2019.yaml", "w") as cat_file:
    yaml.safe_dump(pulsar_dict, cat_file, sort_keys=False, indent=2)