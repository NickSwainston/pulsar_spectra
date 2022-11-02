from pulsar_spectra.catalogue import collect_catalogue_fluxes
from pulsar_spectra.spectral_fit import find_best_spectral_fit

cat_list = collect_catalogue_fluxes()
pulsar = 'J0040+5716'
freqs, bands, fluxs, flux_errs, refs = cat_list[pulsar]
freqs += [300.]
bands += [30.]
fluxs += [10.]
flux_errs += [2.]
refs += ["Your Work"]
find_best_spectral_fit(pulsar, freqs, bands, fluxs, flux_errs, refs, plot_best=True)