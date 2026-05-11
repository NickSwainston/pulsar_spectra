from pulsar_spectra.catalogue import collect_catalogue_fluxes
from pulsar_spectra.spectral_fit import find_best_spectral_fit

cat_dict = collect_catalogue_fluxes()
pulsar = "J0332+5434"
freqs, bands, fluxs, flux_errs, limit_signs, refs = cat_dict[pulsar]

result = find_best_spectral_fit(
    pulsar, freqs, bands, fluxs, flux_errs, limit_signs, refs, plot_best=True
)

print(f"Best fit model: {result.model}")
for p, v in result.params.items():
    e = result.param_errs[p]
    if p.startswith("v"):
        print(f"{p} = {v:.1f} +/- {e:.1f} MHz")
    else:
        print(f"{p} = {v:.5f} +/- {e:.5f}")
