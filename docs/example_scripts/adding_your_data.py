from pulsar_spectra.catalogue import collect_catalogue_fluxes
from pulsar_spectra.spectral_fit import find_best_spectral_fit

cat_list = collect_catalogue_fluxes()
pulsar = 'J0034-0534'
freqs, fluxs, flux_errs, refs = cat_list[pulsar]
freqs += [300.]
fluxs += [32.]
flux_errs += [3.]
refs += ["Your Work"]
find_best_spectral_fit(pulsar, freqs, fluxs, flux_errs, refs, plot_best=True)