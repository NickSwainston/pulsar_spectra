from pulsar_spectra.analysis import estimate_flux_density
from pulsar_spectra.catalogue import collect_catalogue_fluxes
from pulsar_spectra.spectral_fit import find_best_spectral_fit

cat_dict = collect_catalogue_fluxes()
pulsar = "J0820-1350"
freqs, bands, fluxs, flux_errs, refs = cat_dict[pulsar]

best_model_name, _, fit_results, _, _ = find_best_spectral_fit(
    pulsar,
    freqs,
    bands,
    fluxs,
    flux_errs,
    refs,
)

fitted_flux, fitted_flux_err = estimate_flux_density(150.0, best_model_name, fit_results[best_model_name])

print(f"{pulsar} estimated flux: {fitted_flux:.1f} ± {fitted_flux_err:.1f} mJy")
