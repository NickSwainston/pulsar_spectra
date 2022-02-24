import matplotlib.pyplot as plt
from pulsar_spectra.spectral_fit import find_best_spectral_fit
from pulsar_spectra.catalogues import collect_catalogue_fluxes

# Pulsar, flux, flux_err
pulsar_flux = [
    ('J0820-1350', 200, 9,  0),
    ('J0837+0610', 430, 10, 1),
    ('J1453-6413', 630, 20, 2),
    ('J1456-6843', 930, 25, 3),
    ('J1645-0317', 883, 80, 4),
    ('J2018+2839', 100, 10, 5),
]
cols = 2
rows = 3
fig, axs = plt.subplots(nrows=rows, ncols=cols, figsize=(5*cols, 3*rows))

cat_list = collect_catalogue_fluxes()
for pulsar, flux, flux_err, ax_i in pulsar_flux:
    freqs, fluxs, flux_errs, refs = cat_list[pulsar]
    freqs += [150.]
    fluxs += [flux]
    flux_errs += [flux_err]
    refs += ["Your Work"]

    model, m, fit_info, p_best, p_category = find_best_spectral_fit(pulsar, freqs, fluxs, flux_errs, refs, plot_best=True, alternate_style=True, axis=axs[ax_i//cols, ax_i%cols])
    axs[ax_i//cols, ax_i%cols].set_title('PSR '+pulsar)

plt.tight_layout(pad=2.5)
plt.savefig("multi_pulsar_spectra.png", bbox_inches='tight', dpi=300)