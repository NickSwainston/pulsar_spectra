"""
Functions for plotting spectral data and model fits.
"""

import logging

import matplotlib.pyplot as plt
import numpy as np
import yaml
from cycler import cycler
from matplotlib.ticker import FormatStrFormatter

from .catalogue import convert_cat_list_to_dict
from .load_data import DEFAULT_PLOTTING_CONFIG
from .models import model_settings

logger = logging.getLogger(__name__)


def compute_log_lims(vals, val_errs=None, margin=0.1):
    """Compute the plot limits based on data and data error bars.

    Parameters
    ----------
    vals : `list`
        List of data values.
    val_errs : `list`, optional
        List of data value errors. |br| Default: None.
    margin : `float`, optional
        Margin of space beyond min and max data points, in range (0, 1). |br| Default: 0.1.

    Returns
    -------
    plot_lims : `list`
        The plot limits in the form [lower_lim, upper_lim].
    """
    if margin <= 0 or margin >= 1:
        # Margin cannot be greater than the figure size
        print("Invald plot margin. Defaulting to 30%.")
        margin = 0.1

    vals = np.array(vals)

    if val_errs is None:
        val_errs = 0.0
    else:
        val_errs = [x if x is not None else 0 for x in val_errs]
        val_errs = np.array(val_errs)

    # Max and min values including error bars
    lower_vals = vals - val_errs / 2
    upper_vals = vals + val_errs / 2

    # Transform to log space
    log_vals = np.log10(vals, where=vals > 0)
    lower_log_vals = np.log10(lower_vals, where=lower_vals > 0)
    upper_log_vals = np.log10(upper_vals, where=upper_vals > 0)

    # Log limits
    min_log_val = np.min(np.concatenate([lower_log_vals, log_vals]))
    max_log_val = np.max(np.concatenate([upper_log_vals, log_vals]))
    log_range = max_log_val - min_log_val
    log_centre = 0.5 * (max_log_val + min_log_val)

    # Log limits with margins
    expanded_log_range = log_range * (1 + margin)
    expanded_min_log_val = log_centre - 0.5 * expanded_log_range
    expanded_max_log_val = log_centre + 0.5 * expanded_log_range

    # Compute limits in linear space
    lim_lower = 10**expanded_min_log_val
    lim_upper = 10**expanded_max_log_val
    return [lim_lower, lim_upper]


def make_comparison_plot(
    freqs_MHz,
    bands_MHz,
    fluxs_mJy,
    flux_errs_mJy,
    ref_all,
    plot_dicts,
    aic_dict,
    best_fit_model_name=None,
    save_name="comparison_fit.png",
    **plot_kwargs,
):
    """Make a figure showing all of the fitted models together, highlighting
    the best fitting model.

    Parameters
    ----------
    freqs_MHz : `list`
        A list of the frequencies in MHz.
    bands_MHz : `list`
        A list of bandwidths in MHz.
    fluxs_mJy : `list`
        A list of the flux density in mJy.
    flux_errs_mJy : `list`
        A list of the uncertainty of the flux density in mJy.
    ref_all : `list`
        A list of the reference label (in the format 'Author_year').
    plot_dicts : `dict`
        A dictionary with keys for each model name, containing plot dictionaries
        as returned by :py:meth:`pulsar_spectra.frequentist.iminuit_interpolate_model()` or
        :py:meth:`pulsar_spectra.bayesian.bilby_interpolate_model()`.
    aic_dict : `dict`
        A dictionary of AIC values organised by model name.
    best_fit_model_name : `string`, optional
        The name of the best fit model to highlight. |br| Default: None.
    save_name : str, optional
        The filename of the plot to save. |br| Default: 'comparison_fit.png'.
    plot_kwargs : `dict`, optional
        A dictionary of additional kwargs to pass to :py:meth:`pulsar_spectra.plotting.plot_fit()`.
    """
    # Setup figure
    nrows = len(plot_dicts)
    plot_size = 4
    fig, axes = plt.subplots(nrows, 1, figsize=(plot_size, plot_size * nrows))

    for ax, model_name in zip(axes, plot_dicts.keys(), strict=False):
        plot_fit(
            freqs_MHz,
            bands_MHz,
            fluxs_mJy,
            flux_errs_mJy,
            ref_all,
            model_name,
            plot_dicts[model_name],
            axis=ax,
            append_legend=f"\n$\\mathrm{{AICc}}={aic_dict[model_name]:.2f}$",
            **plot_kwargs,
        )

        if best_fit_model_name is not None:
            if model_name == best_fit_model_name:
                rect = plt.Rectangle(
                    # (lower-left corner), width, height
                    (-0.4, -0.13),
                    2.4,
                    1.2,
                    fill=False,
                    color="k",
                    lw=2,
                    zorder=1000,
                    transform=ax.transAxes,
                    figure=fig,
                )
                fig.patches.extend([rect])

    plt.savefig(save_name, bbox_inches="tight", dpi=300)
    plt.close()


def plot_fit(
    freqs_MHz,
    bands_MHz,
    fluxs_mJy,
    flux_errs_mJy,
    ref_all,
    model_name,
    plot_dict,
    save_name="fit.png",
    plot_error=True,
    alternate_style=False,
    axis=None,
    secondary_fit=False,
    fit_range=None,
    ref_markers=None,
    plot_bands=True,
    append_legend=None,
    plotting_config=DEFAULT_PLOTTING_CONFIG,
):
    """Create a plot of the pulsar spectral fit.

    Parameters
    ----------
    freqs_MHz : `list`
        A list of the frequencies in MHz.
    bands_MHz : `list`
        A list of bandwidths in MHz.
    fluxs_mJy : `list`
        A list of the flux density in mJy.
    flux_errs_mJy : `list`
        A list of the uncertainty of the flux density in mJy.
    ref_all : `list`
        A list of the reference label (in the format 'Author_year').
    model_name : `function`
        The model name from :py:meth:`pulsar_spectra.models`.
    plot_dict : `dict`
        A dictionary of data which will be used for plotting, returned by either
        :py:meth:`pulsar_spectra.frequentist.iminuit_interpolate_model()` or
        :py:meth:`pulsar_spectra.bayesian.bilby_interpolate_model()`.
    save_name : `string`, optional
        The name of the saved plot. |br| Default: "fit.png".
    plot_error : `boolean`, optional
        If you want to include the fit error in the plot. |br| Default: True.
    alternate_style : `boolean`, optional
        Plot with the alternate plot style based on Jankowski 2018. |br| Default: False.
    axis : `Axes`, optional
        The axes with which the spectrum will be plotted. |br| None.
    secondary_fit : `boolean`, optional
        Plot model with an alternate style and without markers. |br| Default: False.
    fit_range : `tuple`, (`float`, `float`) optional
        Frequency range to plot the second model over in MHz, eg. (100, 3000).
        |br| Default: None, will use input frequency range.
    ref_markers : `dict` [`string`, `tuple`], optional
        Used to overwrite the data marker defaults.
        The key is the reference name and the tuple contains (color, marker, markersize).
        |br| Default: None.
    plot_bands : `boolean`, optional
        Plot bandwidths as error bars. |br| Default: False.
    append_legend : `str`, optional
        A string to append to the information in the legend. |br| Default: None.
    plotting_config : `string`, optional
        File path of plotting config file. |br| Default: configs/plotting_config.yaml
    """
    if ref_markers is None:
        ref_markers = {}

    with open(plotting_config, "r") as f:
        config = yaml.safe_load(f)

    # Set up plot
    if axis is None:
        fig, ax = plt.subplots(figsize=(config["Figure height"] * config["Aspect ratio"], config["Figure height"]))
    else:
        ax = axis

    # Set up default mpl markers
    custom_cycler = (
        cycler(color=[p[1] for p in config["Markers"]])
        + cycler(marker=[p[2] for p in config["Markers"]])
        + cycler(markersize=[p[3] for p in config["Markers"]])
    )
    ax.set_prop_cycle(custom_cycler)

    # Add data
    data_dict = convert_cat_list_to_dict({"dummy_pulsar": [freqs_MHz, bands_MHz, fluxs_mJy, flux_errs_mJy, ref_all]})[
        "dummy_pulsar"
    ]
    for ref in data_dict.keys():
        if ref in ref_markers.keys():
            # Ref in user defined markers so use theirs
            color, marker, markersize = ref_markers[ref]
        else:
            # Use our defaults
            color = None
            marker = None
            markersize = None
        freqs_ref = np.array(data_dict[ref]["Frequency MHz"])
        if plot_bands and None not in data_dict[ref]["Bandwidth MHz"]:
            bands_ref = np.array(data_dict[ref]["Bandwidth MHz"]) / 2.0
        else:
            bands_ref = None
        if secondary_fit:
            marker_alpha = 0.0
            marker_label = None
        else:
            marker_alpha = 1.0
            marker_label = ref.replace("_", " ")
        fluxs_ref = np.array(data_dict[ref]["Flux Density mJy"])
        flux_errs_ref = np.array(data_dict[ref]["Flux Density error mJy"]) / 2.0
        (_, caps, _) = ax.errorbar(
            freqs_ref,
            fluxs_ref,
            xerr=bands_ref,
            yerr=flux_errs_ref,
            linestyle="None",
            mec="k",
            markeredgewidth=config["Marker border"],
            elinewidth=config["Errorbar linewidth"],
            capsize=config["Capsize"],
            label=marker_label,
            color=color,
            marker=marker,
            markersize=markersize,
            alpha=marker_alpha,
        )
        for cap in caps:
            cap.set_markeredgewidth(config["Errorbar linewidth"])

    fit_info = plot_dict["fit_info"]
    fitted_freqs = plot_dict["fitted_freqs"]
    fitted_flux = plot_dict["fitted_flux"]
    error_type = plot_dict["error_type"]

    if alternate_style:
        # Use the short model name
        model_dict = model_settings()
        fit_info = model_dict[model_name][1]
    else:
        fit_info += append_legend

    # Plot the fit curve
    if secondary_fit:
        ax.plot(
            fitted_freqs,
            fitted_flux,
            config["Model colour"],
            marker="None",
            ls=config["Secondary linestyle"],
            lw=2,
            alpha=0.5,
            label=fit_info,
        )
    else:
        ax.plot(
            fitted_freqs,
            fitted_flux,
            config["Model colour"],
            marker="None",
            ls=config["Primary linestyle"],
            label=fit_info,
        )

    if plot_error:
        if error_type == "jacobi":
            fitted_flux_err = plot_dict["fitted_flux_err"]

            if fitted_flux_err is not None and None not in fitted_flux_err:
                if secondary_fit:
                    alpha = 0
                else:
                    alpha = 0.5

                # Plot 1 sigma error band
                ax.fill_between(
                    fitted_freqs,
                    fitted_flux - fitted_flux_err,
                    fitted_flux + fitted_flux_err,
                    facecolor=config["Model error colour"],
                    alpha=alpha,
                )
        elif error_type == "raytrace":
            fitted_flux_samples = plot_dict["fitted_flux_samples"]

            ax.plot(
                fitted_freqs,
                fitted_flux,
                "k",
                marker="None",
                ls="-",
                lw=0.1,
                alpha=0.1,
                zorder=10,
            )

            for isamp in range(fitted_flux_samples.shape[0]):
                fitted_flux_i = fitted_flux_samples[isamp]

                ax.plot(
                    fitted_freqs,
                    fitted_flux_i,
                    "k",
                    marker="None",
                    ls="-",
                    lw=0.2,
                    alpha=0.1,
                    zorder=0.1,
                )

    # Format plot and save
    ax.set_xscale("log")
    ax.set_yscale("log")
    if plot_bands:
        if fit_range is None:
            ax.set_xlim(compute_log_lims(freqs_MHz, bands_MHz))
        else:
            ax.set_xlim(compute_log_lims(freqs_MHz + [*fit_range], bands_MHz + [0] * 2))
    else:
        ax.set_xlim(compute_log_lims(freqs_MHz))
    ax.set_ylim(compute_log_lims(fluxs_mJy, flux_errs_mJy))
    ax.get_xaxis().set_major_formatter(FormatStrFormatter("%g"))
    ax.get_yaxis().set_major_formatter(FormatStrFormatter("%g"))
    ax.tick_params(which="both", direction="in", top=1, right=1)
    ax.set_xlabel("Frequency (MHz)")
    ax.set_ylabel("Flux Density (mJy)")
    if alternate_style:
        ax.legend(loc="lower left", ncol=2, fontsize=6)
    else:
        ax.legend(loc="center left", bbox_to_anchor=(1.1, 0.5), fontsize=8)
    ax.grid(visible=True, ls=":", lw=0.6)
    if axis is None:
        # Not using axis mode so save figure
        plt.savefig(save_name, bbox_inches="tight", dpi=config["Resolution"])
        plt.close()
