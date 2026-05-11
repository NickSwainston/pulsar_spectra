from pulsar_spectra.catalogue import collect_catalogue_fluxes
from pulsar_spectra.spectral_fit import find_best_spectral_fit

cat_dict = collect_catalogue_fluxes()
pulsar = "J1327-6222"
freqs, bands, fluxs, flux_errs, limit_signs, refs = cat_dict[pulsar]

result = find_best_spectral_fit(
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

print(f"{pulsar} fit: {result.model} (p_best={result.p_best:.3f})")
print("Maximum-posterior parameter values:")
for p, v in result.params.items():
    e = result.param_errs[p]
    if p.startswith("v"):
        print(f"{p} = {v:.1f} +/- {e:.1f} MHz")
    elif p == "c":
        print(f"{p} = {v:.5f} +/- {e:.5f} mJy")
    else:
        print(f"{p} = {v:.5f} +/- {e:.5f}")
