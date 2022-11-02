from pulsar_spectra.catalogue import collect_catalogue_fluxes
from pulsar_spectra.spectral_fit import find_best_spectral_fit

cat_list = collect_catalogue_fluxes()
pulsar = 'J0332+5434'
freqs, bands, fluxs, flux_errs, refs = cat_list[pulsar]
best_model_name, iminuit_result, fit_info, p_best, p_category = find_best_spectral_fit(pulsar, freqs, bands, fluxs, flux_errs, refs, plot_best=True)

print(f"Best fit model: {best_model_name}")
for p, v, e in zip(iminuit_result.parameters, iminuit_result.values, iminuit_result.errors):
    if p.startswith("v"):
        print(f"{p} = {v/1e6:8.1f} +/- {e/1e6:8.1} MHz")
    else:
        print(f"{p} = {v:.5f} +/- {e:.5}")