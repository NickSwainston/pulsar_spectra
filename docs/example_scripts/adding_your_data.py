from pulsar_spectra.catalogues import collect_catalogue_fluxes
from pulsar_spectra.spectral_fit import find_best_spectral_fit

cat_list = collect_catalogue_fluxes()
pulsar = 'J1453-6413'
freqs, fluxs, flux_errs, refs = cat_list[pulsar]
freqs += [150.]
fluxs += [1000.]
flux_errs += [100.]
refs += ["Your Work"]
find_best_spectral_fit(pulsar, freqs, fluxs, flux_errs, refs, plot_best=True)