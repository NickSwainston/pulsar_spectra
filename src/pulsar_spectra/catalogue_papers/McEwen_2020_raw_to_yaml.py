import yaml
import csv
import psrqpy

query = psrqpy.QueryATNF(params=['PSRJ', 'NAME', 'PSRB']).pandas
jnames = list(query['PSRJ'])

with open("McEwen_2020_raw.tsv", "r") as raw_file:
    tsv_file = csv.reader(raw_file, delimiter="\t")
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

    pulsar = row[0].strip().replace("–", "-")
    # Wrong names I found
    if pulsar == "J0038-25":
        pulsar = "J0038-2501"
    elif pulsar == "J0053+69":
        pulsar = "J0054+6946"
    elif pulsar == "J0059+50":
        pulsar = "J0058+4950"
    elif pulsar == "J0100+69":
        pulsar = "J0059+69"
    elif pulsar == "J0112+66":
        pulsar = "J0111+6624"
    elif pulsar == "J0121+14":
        pulsar = "J0122+1416"
    elif pulsar == "J0136+63":
        pulsar = "J0137+6349"
    elif pulsar == "J0325+67":
        pulsar = "J0325+6744"
    elif pulsar == "J0358+42":
        pulsar = "J0358+4155"
    elif pulsar == "J0358+66":
        pulsar = "J0358+6627"
    elif pulsar == "J0510+38":
        pulsar = "J0509+3801"
    elif pulsar == "J0519+54":
        pulsar = "J0518+5416"
    elif pulsar == "J0610+37":
        pulsar = "J0612+37216"
    elif pulsar == "J0709+05":
        pulsar = "J0709+0458"
    elif pulsar == "J0737+69":
        pulsar = "J0738+6904"
    elif pulsar == "J0746+66":
        pulsar = "J0747+6646"
    elif pulsar == "J0943+41":
        pulsar = "J0944+4106"
    elif pulsar == "J1101+65":
        pulsar = "J1059+6459"
    elif pulsar == "J1126-27":
        pulsar = "J1126-2737"
    elif pulsar == "J1134+24":
        pulsar = "J1132+25"
    elif pulsar == "J1235-02":
        pulsar = "J1236-0159"
    elif pulsar == "J1327+34":
        pulsar = "J1326+33"
    elif pulsar == "J1439+76":
        pulsar = "J1439+7655"
    elif pulsar == "J1515-32":
        pulsar = "J1517-32"
    elif pulsar == "J1518-3950":
        pulsar = "J1518-3952"
    elif pulsar == "J1524-33":
        pulsar = "J1523-3235"
    elif pulsar == "J1627+86":
        pulsar = "J1624+8643"
    elif pulsar == "J1629-3827":
        pulsar = "J1629-3825"
    elif pulsar == "J1630+37":
        pulsar = "J1630+3734"
    elif pulsar == "J1647+66":
        pulsar = "J1647+6608"
    elif pulsar == "J1649+80":
        pulsar = "J1641+8049"
    elif pulsar == "J1710+49":
        pulsar = "J1710+4923"
    elif pulsar == "J1815+55":
        pulsar = "J1815+5546"
    elif pulsar == "J1821+41":
        pulsar = "J1821+4147"
    elif pulsar == "J1859+76":
        pulsar = "J1859+7654"
    elif pulsar == "J1901-04":
        pulsar = "J1901-0312"
    elif pulsar == "J1916+32":
        pulsar = "J1916+3224"
    elif pulsar == "J1917-30":
        pulsar = "J1916-2939"
    elif pulsar == "J1921-05B":
        pulsar = "J1921-05"
    elif pulsar == "J1921-05A":
        pulsar = "J1921-0510"
    elif pulsar == "J1921+42":
        pulsar = "J1923+4243"
    elif pulsar == "J1930-01":
        pulsar = "J1931-0144"
    elif pulsar == "J1935+52":
        pulsar = "J1934+5219"
    elif pulsar == "J1939+66":
        pulsar = "J1938+6604"
    elif pulsar == "J1941+0237":
        pulsar = "J1940+0239"
    elif pulsar == "J1941+43":
        pulsar = "J1941+4320"
    elif pulsar == "J1942+81":
        pulsar = "J1942+8106"
    elif pulsar == "J1949+34":
        pulsar = "J1949+3426"
    elif pulsar == "J1953+67":
        pulsar = "J1955+6708"
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
    elif pulsar == "J2122+54":
        pulsar = "J2123+5434"
    elif pulsar == "J2137+64":
        pulsar = "J2137+6428"
    elif pulsar == "J2207+40":
        pulsar = "J2208+4056"
    elif pulsar == "J2210+21":
        pulsar = "J2209+22"
    elif pulsar == "J2229+64":
        pulsar = "J2228+6447"
    elif pulsar == "J2243+69":
        pulsar = "J2241+6941"
    elif pulsar == "J2316+69":
        pulsar = "J2312+6931"
    elif pulsar == "J2329+47":
        pulsar = "J2329+4743"
    elif pulsar == "J2353-22":
        pulsar = "J2354-22"
    elif pulsar == "J2356+22":
        pulsar = "J2355+2246"
    elif pulsar == "J0125-23":
        pulsar = "J0125-2327"
    elif pulsar == "J0636+5129":
        pulsar = "J0636+5128"
    elif pulsar == "J0740+41":
        pulsar = "J0742+4110"
    # elif pulsar == "J1643-10":
    #     pulsar = "J164310"
    elif pulsar == "J2150-03":
        pulsar = "J2150-0326"
    elif pulsar == "J2227+30":
        pulsar = "J2227+3038"
    elif pulsar == "J1654-2636":
        pulsar = "J1654-26"
    elif pulsar == "J0025-19":
        pulsar = "J0026-1955"
    elif pulsar == "J1358-2533":
        pulsar = "J1357-2530"
    elif pulsar == "J1614-23":
        pulsar = "J1614-2318"
    elif pulsar == "J1629+43":
        pulsar = "J1628+4406"


    if pulsar not in jnames:
        print(pulsar)


    flux = round(float(row[1]), 1)
    flux_err = round(float(row[2]), 1)
    pulsar_dict[pulsar] = {
        "Frequency MHz":[350.],
        "Bandwidth MHz":[100.],
        "Flux Density mJy":[flux],
        "Flux Density error mJy":[flux_err]
    }

with open("McEwen_2020.yaml", "w") as cat_file:
    yaml.safe_dump(pulsar_dict, cat_file, sort_keys=False, indent=2)