"""
The top-level function for fitting and selecting spectral models.
"""

import logging

import numpy as np

from .cost_functions import gaussian_cost_function, huber_cost_function, t_cost_function
from .model_selection import select_best_fit_model
from .models import model_settings
from .plotting import make_comparison_plot, plot_fit

logger = logging.getLogger(__name__)


def find_best_spectral_fit(
    pulsar: str,
    freqs_MHz: list,
    bands_MHz: list,
    fluxs_mJy: list,
    flux_errs_mJy: list,
    ref_all: list,
    method: str = "ml",
    likelihood: str = "Huber",
    exclude_models: list = None,
    plot_all: bool = False,
    plot_best: bool = False,
    plot_compare: bool = False,
    plot_bands: bool = True,
    fit_range: tuple[float, float] = None,
    plot_kwargs: dict[str] | None = None,
    sampler_kwargs: dict[str] | None = None,
) -> tuple[str, float, dict, dict, dict]:
    """Find the best-fit spectral model for a given pulsar.

    Parameters
    ----------
    pulsar : `str`
        The Jname of the pulsar to be fit (used for labelling).
    freqs_MHz : `list`
        A list of the frequencies in MHz.
    bands_MHz : `list`
        A list of bandwidths in MHz.
    fluxs_mJy : `list`
        A list of the flux densities in mJy.
    flux_errs_mJy : `list`
        A list of the uncertainties in the flux densities in mJy.
    ref_all : `list`
        A list of the reference labels (in the format 'author_year').
    method : `string`, optional
        The fitting method to use. 'ml' for maximum-likelihood fitting using iminuit
        or 'ns' for Bayesian nested sampling using Bilby/Dynesty. Default: 'ml'.
    likelihood : `string`, optional
        The distribution to use for the likelihood ('Gaussian', 'Huber', 't'). |br| Default: 'Huber'.
    exclude_models : `list`, optional
        A list of models to exclude from :py:meth:`pulsar_spectra.models.model_settings`. Default: `None`.
    plot_all : `bool`, optional
        Make a separate plot for each fitted model. |br| Default: `False`.
    plot_best : `bool`, optional
        Make a plot for the best-fit model. |br| Default: `False`.
    plot_compare : `bool`, optional
        Make a combined plot for all fitted models. |br| Default: `False`.
    plot_bands : `bool`, optional
        Indicate the bandwidth of each measurement using x-axis error bars. |br| Default: `True`.
    fit_range : `tuple[float, float]`, optional
        The range of frequencies (in MHz) to plot the model fit. If `None`, then the
        model fit will be plotted over the frequency span of the data. |br| Default: `None`.
    plot_kwargs : `dict`, optional
        kwargs to pass to :py:meth:`pulsar_spectra.plotting.plot_fit()`.
    sampler_kwargs : `dict`, optional
        kwargs to pass to :py:meth:`bilby.run_sampler()`.

    Returns
    -------
    best_fit_model_name : `str`
        The best fit model name from :py:meth:`pulsar_spectra.models`.
    p_best : `float`
        The probability that the selected model is the best-fitting model out
        of the models compared.
    fit_results : `dict`
        A dictionary of fit results organised by model name.
    aic_dict : `dict`
        A dictionary of AICc values organised by model name.
    plot_dicts : `dict`
        A dictionary of plot dictionaries organised by model name.
    """
    if plot_kwargs is None:
        plot_kwargs = {}
    if sampler_kwargs is None:
        sampler_kwargs = {}

    # Conditional imports
    if method == "ml":
        from .fitters.frequentist import (
            iminuit_compute_likelihood,
            iminuit_fit_spectral_model,
            iminuit_interpolate_model,
        )

        logger.warning(
            "Models will be fit by maximising the likelihood with iminuit. "
            + "For more robust model fits, we recommend using the Bayesian "
            + "nested sampling method. See the help for "
            + "pulsar_spectra.spectral_fit.find_best_spectral_fit() for details."
        )
    elif method == "ns":
        from .fitters.bayesian import (
            bilby_compute_maximum_posterior_likelihood,
            bilby_fit_spectral_model,
            bilby_interpolate_model,
        )
    else:
        logger.error(f"Invalid fitting method: {method}.")
        return None, None, None, None, None

    # Cost function (i.e. negative log-likelihood)
    if likelihood == "Gaussian":
        cost_function = gaussian_cost_function
    elif likelihood == "Huber":
        cost_function = huber_cost_function
    elif likelihood == "t":
        cost_function = t_cost_function
    else:
        logger.error(f"Invalid likelihood: {likelihood}.")
        return None, None, None, None, None

    if exclude_models is None:
        exclude_models = []

    # Load model settings
    model_dict = model_settings()

    # Create fit line
    if fit_range is None:
        # No fit range given so use full range
        if plot_bands and None not in bands_MHz:
            # TODO: Scale to bands even with Nones in bands array
            min_freqs_MHz = np.min(np.array(freqs_MHz) - np.array(bands_MHz) / 2)
            max_freqs_MHz = np.max(np.array(freqs_MHz) + np.array(bands_MHz) / 2)
        else:
            min_freqs_MHz = min(freqs_MHz)
            max_freqs_MHz = max(freqs_MHz)
        fitted_freq = np.logspace(np.log10(min_freqs_MHz), np.log10(max_freqs_MHz), 100)
    else:
        # Use input fit range
        min_freq, max_freq = fit_range
        fitted_freq = np.logspace(np.log10(min_freq), np.log10(max_freq), 100)

    # Loop over models and fit
    fit_results = {}
    plot_dicts = {}
    beta_mins = {}
    for model_name in model_dict.keys():
        if model_name in exclude_models:
            continue

        if method == "ml":
            fit_result, band_bool = iminuit_fit_spectral_model(
                freqs_MHz,
                bands_MHz,
                fluxs_mJy,
                flux_errs_mJy,
                model_name=model_name,
                likelihood=likelihood,
            )
            if fit_result is None:
                continue
            beta_min = iminuit_compute_likelihood(
                freqs_MHz,
                bands_MHz,
                fluxs_mJy,
                flux_errs_mJy,
                fit_result,
                model_name,
                band_bool,
                cost_function,
            )
            plot_dict = iminuit_interpolate_model(
                fit_result,
                model_name,
                fitted_freq,
                band_bool,
            )
        elif method == "ns":
            fit_result = bilby_fit_spectral_model(
                freqs_MHz,
                bands_MHz,
                fluxs_mJy,
                flux_errs_mJy,
                model_name=model_name,
                likelihood=likelihood,
                label=pulsar,
                **sampler_kwargs,
            )
            band_bool = True
            if fit_result is None:
                continue
            beta_min, params_beta_min = bilby_compute_maximum_posterior_likelihood(
                freqs_MHz,
                bands_MHz,
                fluxs_mJy,
                flux_errs_mJy,
                fit_result,
                model_name,
                band_bool,
                cost_function,
            )
            plot_dict = bilby_interpolate_model(
                fit_result,
                model_name,
                fitted_freq,
                params_beta_min,
            )
        fit_results[model_name] = fit_result
        plot_dicts[model_name] = plot_dict
        beta_mins[model_name] = beta_min

    if len(fit_results.keys()) == 0:
        return None, None, None, None, None

    # Select the best-fit model out of those fitted
    aic_dict, best_fit_model_name, p_best = select_best_fit_model(beta_mins, len(freqs_MHz))

    # Create spectra plot(s)
    if plot_best:
        # Plot just the best-fit model
        fit_info = f"\n$\\mathrm{{AICc}}={aic_dict[best_fit_model_name]:.2f}$" + f"\n$p_\\mathrm{{best}}={p_best:.3f}$"
        plot_fit(
            freqs_MHz,
            bands_MHz,
            fluxs_mJy,
            flux_errs_mJy,
            ref_all,
            best_fit_model_name,
            plot_dicts[best_fit_model_name],
            save_name=f"{pulsar}_{best_fit_model_name}_fit.png",
            append_legend=fit_info,
            **plot_kwargs,
        )
    elif plot_compare:
        # Plot all fitted models side-by-side
        make_comparison_plot(
            freqs_MHz,
            bands_MHz,
            fluxs_mJy,
            flux_errs_mJy,
            ref_all,
            plot_dicts,
            aic_dict,
            best_fit_model_name=best_fit_model_name,
            save_name=f"{pulsar}_comparison_fit.png",
            **plot_kwargs,
        )
    elif plot_all:
        # Plot all model fits individually
        for model_name in model_dict.keys():
            plot_fit(
                freqs_MHz,
                bands_MHz,
                fluxs_mJy,
                flux_errs_mJy,
                ref_all,
                model_name,
                plot_dicts[model_name],
                save_name=f"{pulsar}_{model_name}_fit.png",
                append_legend=f"\n$\\mathrm{{AICc}}={aic_dict[model_name]:.2f}$",
                **plot_kwargs,
            )

    return best_fit_model_name, p_best, fit_results, aic_dict, plot_dicts
