import matplotlib.pyplot as plt
import numpy as np

from pulsar_spectra.catalogue import collect_catalogue_fluxes
from pulsar_spectra.models import double_turn_over_spectrum
from pulsar_spectra.spectral_fit import find_best_spectral_fit, propagate_flux_n_err

# v1.4
cat_dict = collect_catalogue_fluxes()
pulsar = "J1852-0635"
freqs, fluxs, flux_errs, refs = cat_dict[pulsar]
best_model_name, iminuit_result, fit_info, p_best, p_category = find_best_spectral_fit(
    pulsar, freqs, fluxs, flux_errs, refs
)

# Cherry picked data
freqs = [650, 1400.29, 5000]
fluxs = [7.0, 11.97, 4.686]
flux_errs = [0.7, 1.197, 0.44]
refs = ["Dembska_2014_ATNF", "Han_2016", "Dembska_2014_ATNF"]
colours = ["#00435b", "#0cc0ff", "#0dc3c6"]

# Set up default mpl markers
capsize = 10
errorbar_linewidth = 5
marker_border_thickness = 0
plotsize = 3.2

for line_colour in ("black", "white"):
    # Set up plot
    fig, ax = plt.subplots(figsize=(plotsize, plotsize))
    # plot data
    for freq, flux, flux_err, color in zip(freqs, fluxs, flux_errs, colours):
        (_, caps, _) = ax.errorbar(
            freq,
            flux,
            yerr=flux_err * 3,
            linestyle="None",
            mec="k",
            markeredgewidth=marker_border_thickness,
            elinewidth=errorbar_linewidth,
            capsize=capsize,
            color=color,
            marker="s",
            markersize=20,
        )
        for cap in caps:
            cap.set_markeredgewidth(errorbar_linewidth)

    # Create fit line
    fitted_freq = np.logspace(np.log10(600), np.log10(8000), 100)
    fitted_flux, fitted_flux_prop = propagate_flux_n_err(fitted_freq, double_turn_over_spectrum, iminuit_result)
    ax.plot(fitted_freq, fitted_flux, line_colour, label=fit_info, linewidth=3, zorder=0.5)

    # Format plot and save
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.axis("off")

    plt.savefig(f"logos/logo_{line_colour}.png", bbox_inches="tight", dpi=300, transparent=True)
    plt.savefig(f"logos/logo_{line_colour}.svg", bbox_inches="tight", dpi=300, transparent=True)
    plt.clf()
