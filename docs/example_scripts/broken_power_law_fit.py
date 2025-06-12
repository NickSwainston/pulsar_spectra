from pulsar_spectra.catalogue import collect_catalogue_fluxes
from pulsar_spectra.spectral_fit import iminuit_fit_spectral_model

cat_list = collect_catalogue_fluxes()
pulsar = "J1453-6413"
freqs, fluxs, flux_errs, refs = cat_list[pulsar]

# Broken power law function is in the format
# broken_power_law(v, vb, a1, a2, b, v0)

# start params for (v, vb, a1, a2, b)
start_params = (5e8, -1.6, -1.6, 0.1)

# Fit param limits (min, max) or (v, vb, a1, a2, b)
mod_limits = [(None, None), (-10, 10), (-10, 0), (0, None)]
# None means there is no limit

aic, iminuit_result, fit_info = iminuit_fit_spectral_model(
    freqs,
    fluxs,
    flux_errs,
    refs,
    model_name="broken_power_law",
    start_params=start_params,
    mod_limits=mod_limits,
    plot=True,
    save_name="J1453-6413_broken_power_law.png",
)
