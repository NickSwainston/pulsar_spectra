from pulsar_spectra.spectral_fit import find_best_spectral_fit, estimate_flux_density
from pulsar_spectra.catalogue import collect_catalogue_fluxes

cat_dict = collect_catalogue_fluxes()
pulsar = 'J0820-1350'
freqs, bands, fluxs, flux_errs, refs = cat_dict[pulsar]
model, m, _, _, _ = find_best_spectral_fit(pulsar, freqs, bands, fluxs, flux_errs, refs, plot_best=True)
fitted_flux, fitted_flux_err = estimate_flux_density(150., model, m)
print(f"{pulsar} estimated flux: {fitted_flux:.1f} ± {fitted_flux_err:.1f} mJy")