from pulsar_spectra.catalogue import collect_catalogue_fluxes
from pulsar_spectra.fitters.bayesian import bilby_compute_maximum_posterior_likelihood
from pulsar_spectra.likelihoods import t_cost_function
from pulsar_spectra.spectral_fit import find_best_spectral_fit

cat_dict = collect_catalogue_fluxes()
pulsar = "J1327-6222"
freqs, bands, fluxs, flux_errs, limit_signs, refs = cat_dict[pulsar]

best_model_name, p_best, fit_results, _, _ = find_best_spectral_fit(
    pulsar,
    freqs,
    bands,
    fluxs,
    flux_errs,
    limit_signs,
    refs,
    plot_best=True,
    method="bayesian-nested-sampling",
    likelihood="t",
    sampler_kwargs={"npool": 10},
)

beta_min, params_beta_min = bilby_compute_maximum_posterior_likelihood(
    freqs,
    bands,
    fluxs,
    flux_errs,
    fit_results[best_model_name],
    best_model_name,
    True,
    t_cost_function,
)

print(f"{pulsar} fit: {best_model_name} (p_best={p_best:.3f})")
print("Maximum-likelihood parameter values:")
for p in params_beta_min.keys():
    v = params_beta_min[p]
    if p.startswith("v"):
        print(f"{p} = {v / 1e6:.1f} MHz")
    elif p == "c":
        print(f"{p} = {v:.5f} mJy")
    else:
        print(f"{p} = {v:.5f}")