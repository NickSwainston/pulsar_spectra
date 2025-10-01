from pulsar_spectra.catalogue import collect_catalogue_fluxes

cat_dict = collect_catalogue_fluxes(only_use=["Bates_2011"])

freq, band, flux, flux_err, ref = cat_dict["J1316-6232"]
print(f"J1316-6232 flux: {flux[0]} ± {flux_err[0]} mJy")
freq, band, flux, flux_err, ref = cat_dict["J1327-6222"]
print(f"J1327-6222 flux: {flux[0]} ± {flux_err[0]} mJy")
