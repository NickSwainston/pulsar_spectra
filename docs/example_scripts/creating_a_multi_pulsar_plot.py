import matplotlib.pyplot as plt
from pulsar_spectra.spectral_fit import find_best_spectral_fit
from pulsar_spectra.catalogue import collect_catalogue_fluxes

# Pulsar, flux, flux_err
pulsar_flux = [
    ("J0820-1350", 200, 9, 0),
    ("J0837+0610", 430, 10, 1),
    ("J1453-6413", 630, 20, 2),
    ("J1456-6843", 930, 25, 3),
    ("J1645-0317", 983, 80, 4),
    ("J2018+2839", 100, 10, 5),
]
cols = 2
rows = 3
fig, axs = plt.subplots(nrows=rows, ncols=cols, figsize=(6 * cols, 4 * rows))

cat_dict = collect_catalogue_fluxes()
for pulsar, flux, flux_err, ax_i in pulsar_flux:
    freqs, bands, fluxs, flux_errs, refs = cat_dict[pulsar]
    freqs = [150.0] + freqs
    bands = [10.0] + bands
    fluxs = [flux] + fluxs
    flux_errs = [flux_err] + flux_errs
    refs = ["Your Work"] + refs

    find_best_spectral_fit(
        pulsar,
        freqs,
        bands,
        fluxs,
        flux_errs,
        refs,
        plot_best=True,
        legend_style="compact",
        plot_kwargs={"axis": axs[ax_i // cols, ax_i % cols]},
    )
    axs[ax_i // cols, ax_i % cols].set_title("PSR " + pulsar)

fig.tight_layout(pad=2.5)
fig.savefig("multi_pulsar_spectra.png", bbox_inches="tight", dpi=300)
