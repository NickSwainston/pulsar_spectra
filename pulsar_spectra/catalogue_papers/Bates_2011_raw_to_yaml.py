import json

def replace_zero_err(fluxs, flux_errs):
    new_flux_errs = []
    for i, flux_err in enumerate(flux_errs):
        if flux_err == 0:
            new_flux_errs.append(0.5*fluxs[i])
        else:
            new_flux_errs.append(flux_err)
    return new_flux_errs

with open("Bates_2011_raw.txt", "r") as raw_file:
    lines = raw_file.readlines()

pulsar_dict = {}
for row in lines[:16]:
    row = row.split()
    print(row)
    pulsar = row[0].replace("−", "-")

    flux, flux_err = row[4].split("(")
    sig_fig = len(flux.split(".")[-1])
    pulsar_dict[pulsar] = {"Frequency MHz":[1400],
                           "Flux Density mJy":[float(flux)],
                           "Flux Density error mJy":[round(float(flux_err[:-1]) * 10**(-sig_fig), 4)]}

for row in lines[17:]:
    row = row.split()
    print(row)
    pulsar = row[0].replace("−", "-")

    freqs = [1400, 4850, 6500]
    pulsar_dict[pulsar] = {"Frequency MHz":[],
                           "Flux Density mJy":[],
                           "Flux Density error mJy":[]}
    for freq, pair in zip(freqs, row[6:-1]):
        print(freq,pair)
        if "(" in pair:
            flux, flux_err = pair.split("(")
            sig_fig = len(flux.split(".")[-1])
            pulsar_dict[pulsar]["Frequency MHz"] += [float(freq)]
            pulsar_dict[pulsar]["Flux Density mJy"] += [float(flux)]
            pulsar_dict[pulsar]["Flux Density error mJy"] += [round(float(flux_err[:-1]) * 10**(-sig_fig), 4)]
            pulsar_dict[pulsar]["Flux Density error mJy"] = replace_zero_err(
                pulsar_dict[pulsar]["Flux Density mJy"], 
                pulsar_dict[pulsar]["Flux Density error mJy"]
            )

json = json.dumps(pulsar_dict, indent=4)
with open("Bates_2011.yaml", "w") as cat_file:
    cat_file.write(json)
print(pulsar_dict)