from pulsar_spectra.catalogue import collect_catalogue_fluxes
from pulsar_spectra.spectral_fit import estimate_flux_density, find_best_spectral_fit

cat_dict = collect_catalogue_fluxes()
pulsar = "J0820-1350"
freqs, bands, fluxs, flux_errs, refs = cat_dict[pulsar]
model, m, _, _, _ = find_best_spectral_fit(pulsar, freqs, bands, fluxs, flux_errs, refs, plot_best=True)
fitted_flux, fitted_flux_err = estimate_flux_density(150.0, model, m)
print(f"{pulsar} estimated flux: {fitted_flux:.1f} ± {fitted_flux_err:.1f} mJy")
