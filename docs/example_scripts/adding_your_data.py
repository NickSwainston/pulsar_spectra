from pulsar_spectra.catalogue import collect_catalogue_fluxes
from pulsar_spectra.spectral_fit import find_best_spectral_fit

cat_list = collect_catalogue_fluxes()
pulsar = "J0040+5716"
freqs, bands, fluxs, flux_errs, limit_signs, refs = cat_list[pulsar]
freqs = [300.0] + freqs
bands = [30.0] + bands
fluxs = [10.0] + fluxs
flux_errs = [2.0] + flux_errs
limit_signs = [0] + limit_signs
refs = ["Your Work"] + refs

best_model_name, p_best, fit_results, aic_dict, plot_dicts = find_best_spectral_fit(
    pulsar, freqs, bands, fluxs, flux_errs, limit_signs, refs, plot_best=True
)
