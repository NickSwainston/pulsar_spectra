from pulsar_spectra.catalogue import collect_catalogue_fluxes
from pulsar_spectra.spectral_fit import find_best_spectral_fit

cat_dict = collect_catalogue_fluxes()
pulsar = "J0332+5434"
freqs, bands, fluxs, flux_errs, refs = cat_dict[pulsar]

best_model_name, p_best, fit_results, aic_dict, plot_dicts = find_best_spectral_fit(
    pulsar, freqs, bands, fluxs, flux_errs, refs, plot_best=True
)

result = fit_results[best_model_name]

print(f"Best fit model: {best_model_name}")
for p, v, e in zip(result.parameters, result.values, result.errors):
    if p.startswith("v"):
        print(f"{p} = {v / 1e6:.1f} +/- {e / 1e6:.1f} MHz")
    else:
        print(f"{p} = {v:.5f} +/- {e:.5f}")
