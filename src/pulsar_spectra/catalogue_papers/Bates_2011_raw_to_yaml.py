import yaml

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

for row in lines[17:]:
    row = row.split()
    print(row)
    pulsar = row[0].replace("−", "-")
    # grab last row with an uncertainty
    for pair in row[6:-2]:
        if "(" in pair:
            flux, flux_err = pair.split("(")
            if "." in flux:
                sig_fig = len(flux.split(".")[-1])
            else:
                sig_fig = 0
            pulsar_dict[pulsar] = {
                "Frequency MHz":[6591],
                "Bandwidth MHz":[576],
                "Flux Density mJy":[float(flux)],
                "Flux Density error mJy":[round(float(flux_err[:-1]) * 10**(-sig_fig), 4)]
            }

with open("Bates_2011.yaml", "w") as cat_file:
    yaml.safe_dump(pulsar_dict, cat_file, sort_keys=False, indent=2)