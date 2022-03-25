import json
import psrqpy

with open("Malofeev_2000_raw.txt", "r") as raw_file:
    lines = raw_file.readlines()
query = psrqpy.QueryATNF(params=['PSRJ', 'NAME', 'PSRB']).pandas

pulsar_dict = {}
for row in lines:
    row = row.replace(" + ", "+").replace("J ", "J").replace("MP ","").split()
    print(row)

    pulsar = row[0].replace("–", "-")
    if pulsar != "IP":
        if "J" not in pulsar:
            bname = "B" + pulsar
            pid = list(query['PSRB']).index(bname)
            pulsar = query['PSRJ'][pid]
        if "<" not in row[1]:
            pulsar_dict[pulsar] = {"Frequency MHz":[102.5],
                                "Flux Density mJy":[float(row[1].replace("(", "").replace(")", ""))],
                                "Flux Density error mJy":[float(row[2])]}
    
    pi = None
    for i in range(1, len(row)):
        if ("+" in row[i] or "–" in row[i]) and row[i][0] != "–":
            pi = i
            break
    if pi:
        pulsar = row[pi].replace("–", "-")
        if "IP" in pulsar:
            continue
        if "J" not in pulsar:
            if pulsar == "2044+46":
                pulsar = "J2044+4614"
            else:
                bname = "B" + pulsar
                pid = list(query['PSRB']).index(bname.upper())
            pulsar = query['PSRJ'][pid]
        
        if "<" not in row[pi+1] and ">" not in row[pi+1]:
            pulsar_dict[pulsar] = {"Frequency MHz":[102.5],
                                "Flux Density mJy":[float(row[pi+1].replace("(", "").replace(")", ""))],
                                "Flux Density error mJy":[float(row[pi+2].replace("(", "").replace(")", ""))]}

with open("Malofeev_2000.json", "w") as cat_file:
    cat_file.write(json.dumps(pulsar_dict))
print(pulsar_dict)