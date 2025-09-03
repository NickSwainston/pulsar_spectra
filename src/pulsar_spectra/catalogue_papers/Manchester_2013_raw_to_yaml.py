import yaml

with open("Manchester_2013_raw.txt") as file:
    pulsar_dict = {}
    lines = file.readlines()

for row in lines:
    row = [item.strip() for item in row.split(" ")]

    pulsar = row[0].replace("−", "-")
    s700 = row[5]
    s700_err = row[6]
    s1400 = row[7]
    s1400_err = row[8]
    s3100 = row[9]
    s3100_err = row[10]

    freqs = []
    bands = []
    fluxes = []
    flux_errs = []

    data_freqs = [700.0, 1400.0, 3100.0]
    data_bands = [70.0, 400.0, 1000.0]
    data_fluxes = [float(s700), float(s1400), float(s3100)]
    data_flux_errs = [float(s700_err), float(s1400_err), float(s3100_err)]
    for freq, band, flux, flux_err in zip(data_freqs, data_bands, data_fluxes, data_flux_errs, strict=True):
        if flux_err / flux > 0.5:
            print(f"Clipping PSR {pulsar} at {freq} MHz: flux_err/flux={flux_err / flux:.2f}")
            flux_err = 0.5 * flux
        freqs += [freq]
        bands += [band]
        fluxes += [flux]
        flux_errs += [flux_err]

    pulsar_dict[pulsar] = {
        "Frequency MHz": freqs,
        "Bandwidth MHz": bands,
        "Flux Density mJy": fluxes,
        "Flux Density error mJy": flux_errs,
    }

with open("Manchester_2013.yaml", "w") as cat_file:
    yaml.safe_dump(pulsar_dict, cat_file, sort_keys=False, indent=2)
