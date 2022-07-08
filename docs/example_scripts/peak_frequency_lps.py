from pulsar_spectra.spectral_fit import find_best_spectral_fit
from pulsar_spectra.catalogue import collect_catalogue_fluxes
from pulsar_spectra.analysis import calc_log_parabolic_spectrum_max_freq

cat_dict = collect_catalogue_fluxes()
pulsar = 'J1136+1551'
freqs, fluxs, flux_errs, refs = cat_dict[pulsar]
model_name, m, _, _, _ = find_best_spectral_fit(pulsar, freqs, fluxs, flux_errs, refs)
if model_name == "log_parabolic_spectrum":
    v_peak, u_v_peak = calc_log_parabolic_spectrum_max_freq(
        m.values["a"],
        m.values["b"],
        m.values["v0"],
        m.errors["a"],
        m.errors["b"],
        m.covariance[0][1],
    )
    print(f"v_peak (MHz): {v_peak/1e6:6.2f} +/- {u_v_peak/1e6:6.2f}")
else:
    print("Not a log parabolic spectrum fit")