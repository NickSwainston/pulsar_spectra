from pulsar_spectra.analysis import calc_log_parabolic_spectrum_max_freq
from pulsar_spectra.catalogue import collect_catalogue_fluxes
from pulsar_spectra.spectral_fit import find_best_spectral_fit

cat_dict = collect_catalogue_fluxes()
pulsar = "J1136+1551"
freqs, bands, fluxs, flux_errs, limit_signs, refs = cat_dict[pulsar]

best_model_name, _, fit_results, _, _ = find_best_spectral_fit(
    pulsar,
    freqs,
    bands,
    fluxs,
    flux_errs,
    limit_signs,
    refs,
)

if best_model_name == "log_parabolic_spectrum":
    result = fit_results[best_model_name]

    v_peak, u_v_peak = calc_log_parabolic_spectrum_max_freq(
        result.values["a"],
        result.values["b"],
        result.values["v0"],
        result.errors["a"],
        result.errors["b"],
        result.covariance[0][1],
    )
    print(f"v_peak (MHz): {v_peak / 1e6:.2f} +/- {u_v_peak / 1e6:.2f}")
else:
    print("Not a log parabolic spectrum fit")
