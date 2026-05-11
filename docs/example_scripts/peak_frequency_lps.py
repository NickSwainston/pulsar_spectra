from pulsar_spectra.analysis import calc_log_parabolic_spectrum_max_freq
from pulsar_spectra.catalogue import collect_catalogue_fluxes
from pulsar_spectra.spectral_fit import find_best_spectral_fit

cat_dict = collect_catalogue_fluxes()
pulsar = "J1136+1551"
freqs, bands, fluxs, flux_errs, limit_signs, refs = cat_dict[pulsar]

fit_result = find_best_spectral_fit(
    pulsar,
    freqs,
    bands,
    fluxs,
    flux_errs,
    limit_signs,
    refs,
)

if fit_result.model == "log_parabolic_spectrum":

    v_peak, u_v_peak = calc_log_parabolic_spectrum_max_freq(
        fit_result.params["a"],
        fit_result.params["b"],
        fit_result.params["v0"],
        fit_result.param_errs["a"],
        fit_result.param_errs["b"],
        fit_result.fit_results[fit_result.model].covariance[0][1],
    )
    print(f"v_peak (MHz): {v_peak / 1e6:.2f} +/- {u_v_peak / 1e6:.2f}")
else:
    print(f"Best model was {fit_result.model}, not a log parabolic spectrum fit")
