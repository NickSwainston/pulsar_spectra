from pulsar_spectra.catalogue import collect_catalogue_fluxes
from pulsar_spectra.spectral_fit import find_best_spectral_fit

cat_dict = collect_catalogue_fluxes()
pulsar = 'J1327-6222'
freqs, bands, fluxs, flux_errs, refs = cat_dict[pulsar]

best_model_name, p_best, fit_results, aic_dict, plot_dicts = find_best_spectral_fit(
    pulsar,
    freqs,
    bands,
    fluxs,
    flux_errs,
    refs,
    plot_compare=True,
)