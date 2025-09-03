import yaml
import psrqpy

with open("van_Ommen_1997_raw.txt", "r") as raw_file:
    lines = raw_file.readlines()
query = psrqpy.QueryATNF(params=['PSRJ', 'NAME', 'PSRB']).pandas

pulsar_dict = {}
for row in lines:
    row = row.replace(" + ", "+").split()
    print(row)

    if "-" in row[0] or "+" in row[0]:
        bname = "B" + row[0][:7].replace("–", "-")
        pid = list(query['PSRB']).index(bname)
        pulsar = query['PSRJ'][pid]
        obs_period = row[-12]
        if obs_period == "1979":
            pe = .1
        elif obs_period == "1989" or obs_period == "1990":
            pe = .08
        elif obs_period == "1991":
            pe = .3
        flux = float(row[-8].replace("'", ""))
        pulsar_dict[pulsar] = {
            "Frequency MHz":[float(row[-11])],
            "Bandwidth MHz":[float(row[-10])],
            "Flux Density mJy":[flux],
            "Flux Density error mJy":[round(flux*pe, 4)]
        }
    else:
        obs_period = row[0]
        if obs_period == "1979":
            pe = .1
        elif obs_period == "1989" or obs_period == "1990":
            pe = .08
        elif obs_period == "1991":
            pe = .3
        flux = float(row[4].replace("'", ""))
        pulsar_dict[pulsar]["Frequency MHz"] += [float(row[1])]
        pulsar_dict[pulsar]["Bandwidth MHz"] += [float(row[2])]
        pulsar_dict[pulsar]["Flux Density mJy"] += [flux]
        pulsar_dict[pulsar]["Flux Density error mJy"] += [round(flux*pe, 4)]


with open("van_Ommen_1997.yaml", "w") as cat_file:
    yaml.safe_dump(pulsar_dict, cat_file, sort_keys=False, indent=2)