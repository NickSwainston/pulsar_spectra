"""
The top-level function for finding the best-fit spectral model.
"""

import logging

import numpy as np

from .cost_functions import gaussian_cost_function, huber_cost_function, t_cost_function
from .model_selection import select_best_fit_model
from .models import model_settings
from .plotting import make_comparison_plot, plot_fit

logger = logging.getLogger(__name__)


def find_best_spectral_fit(
    pulsar,
    freqs_MHz,
    bands_MHz,
    fluxs_mJy,
    flux_errs_mJy,
    ref_all,
    method="ml",
    likelihood="Huber",
    exclude_models=None,
    plot_all=False,
    plot_best=False,
    plot_compare=False,
    plot_bands=True,
    fit_range=None,
    sampler_kwargs=None,
    **plot_kwargs,
):
    """Find the best-fit spectral model for a given pulsar.

    Parameters
    ----------
    pulsar : `str`
        The name of the pulsar to be fit (used for labelling).
    freqs_MHz : `array_like`
        An array of the frequencies in MHz.
    bands_MHz : `array_like`
        An array of the bandwidths in MHz.
    fluxs_mJy : `array_like`
        An array of the flux densities in mJy.
    flux_errs_mJy : `array_like`
        An array of the uncertainties in the flux densities in mJy.
    ref_all : `array_like`
        An array of the reference labels (in the format 'author_year').
    method : `str`, optional
        The fitting method to use. The options are as follows:

            'ml' : maximum-likelihood estimation using iminuit.

            'ns' : Bayesian nested sampling using Bilby and Dynesty.

        |br| Default: 'ml'.
    likelihood : `str`, optional
        The likelihood distribution to use. The options are as follows:

            'Gaussian' : A Gaussian distribution (i.e. ordinary least-squares).

            'Huber' : A Gaussian distribution with Huber loss.

            't' : A Student-t distribution with 4 degrees of freedom.

        |br| Default: 'Huber'.
    exclude_models : `list[str]`, optional
        A list of model names to exclude from
        :py:meth:`pulsar_spectra.models.model_settings`. |br| Default: `None`.
    plot_all : `bool`, optional
        Make a separate plot for each fitted model. |br| Default: `False`.
    plot_best : `bool`, optional
        Make a plot for the best-fit model only. |br| Default: `False`.
    plot_compare : `bool`, optional
        Make a combined plot for all fitted models. |br| Default: `False`.
    plot_bands : `bool`, optional
        Indicate the bandwidth of each measurement using x-axis error bars.
        |br| Default: `True`.
    fit_range : `tuple[float, float]`, optional
        The range of frequencies (in MHz) to plot the model fit. If `None`, then
        the model fit will be plotted over the frequency span of the data.
        |br| Default: `None`.
    sampler_kwargs : `dict[str, Any]`, optional
        Extra arguments to pass to `bilby.run_sampler()`.
    **plot_kwargs
        Extra arguments to pass to :py:meth:`pulsar_spectra.plotting.plot_fit()`.

    Returns
    -------
    best_fit_model_name : `str`
        The best fit model name from :py:meth:`pulsar_spectra.models`.
    p_best : `float`
        The probability that the selected model is the best-fitting model out
        of the models compared.
    fit_results : `dict[str, iminuit.Minuit | bilby.core.result.Result]`
        A dictionary of fit results with the keys being model names from
        :py:meth:`pulsar_spectra.models.model_settings`.
    aic_dict : `dict[str, float]`
        A dictionary of AICc values with the keys being model names from
        :py:meth:`pulsar_spectra.models.model_settings`.
    plot_dicts : `dict[str, dict[str, Any]]`
        A dictionary of plot dictionaries with the keys being model names from
        :py:meth:`pulsar_spectra.models.model_settings`.
    """
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
            save_name=f"{pulsar}_{best_fit_model_name}_{method}_{likelihood}_fit.png",
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
            save_name=f"{pulsar}_{method}_{likelihood}_comparison_fit.png",
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
                save_name=f"{pulsar}_{model_name}_{method}_{likelihood}_fit.png",
                append_legend=f"\n$\\mathrm{{AICc}}={aic_dict[model_name]:.2f}$",
                **plot_kwargs,
            )

    return best_fit_model_name, p_best, fit_results, aic_dict, plot_dicts
