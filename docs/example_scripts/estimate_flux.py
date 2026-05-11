from pulsar_spectra.analysis import estimate_flux_density
from pulsar_spectra.catalogue import collect_catalogue_fluxes
from pulsar_spectra.spectral_fit import find_best_spectral_fit

cat_dict = collect_catalogue_fluxes()
pulsar = "J0820-1350"
freqs, bands, fluxs, flux_errs, limit_signs, refs = cat_dict[pulsar]

result = find_best_spectral_fit(
    pulsar,
    freqs,
    bands,
    fluxs,
    flux_errs,
    limit_signs,
    refs,
)

fitted_flux, fitted_flux_err = estimate_flux_density(150.0, result.model, result.fit_results[result.model])

print(f"{pulsar} estimated flux: {fitted_flux:.1f} ± {fitted_flux_err:.1f} mJy")
