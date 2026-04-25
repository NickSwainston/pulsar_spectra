"""
The top-level function for finding the best-fit spectral model.
"""

import logging

import numpy as np

from pulsar_spectra.likelihood_functions import gaussian_cost_function, huber_cost_function, t_cost_function
from pulsar_spectra.model_selection import select_best_fit_model
from pulsar_spectra.models import model_settings
from pulsar_spectra.plotting import make_comparison_plot, plot_fit

logger = logging.getLogger(__name__)


def find_best_spectral_fit(
    pulsar,
    freqs_MHz,
    bands_MHz,
    fluxs_mJy,
    flux_errs_mJy,
    limit_signs,
    ref_all,
    method="maximum-likelihood",
    likelihood="Huber",
    exclude_models=None,
    plot_all=False,
    plot_best=False,
    plot_compare=False,
    plot_bands=True,
    fit_range=None,
    legend_style="raw",
    legend_point_estimate="max-std",
    sampler_kwargs=None,
    plot_kwargs=None,
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
        The fitting method to use. The options are:

            'maximum-likelihood' : maximum-likelihood estimation using iminuit.

            'bayesian-nested-sampling' : Bayesian nested sampling using Bilby
            and Dynesty.

        |br| Default: 'maximum-likelihood'.
    likelihood : `str`, optional
        The likelihood distribution to use. The options are:

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
    legend_style : `str`, optional
        The style of the legend in the spectral fit plots. For all legend
        styles, the AICc will be printed for `plot_all` and `plot_compare`, and
        :math:`p_\mathrm{best}` will be printed for `plot_best`. The spectral
        data will always be labelled. The options are:

            'raw' : Print the model and parameters as they are named within the
            code and indicate whether the bandwidth fitting was used. The legend
            will be placed outside of the bbox.

            'typeset' : Print the model and parameters typeset using LaTeX. The
            legend will be placed outside of the bbox.

            'compact' : Print the abbreviated model name. The legend will be
            placed within the bbox.

        |br| Default: 'raw'.
    legend_point_estimate : `str`, optional
        The point estimate of the posterior distribution reported in the legend.
        The options are:

            'max-std' : The maximum of each marginal distribution with
            uncertainties equal to 1 standard deviation.

            'med-ci' : The median of each marginal distribution with
            uncertainties calculated from the 68% credible interval.

        |br| Default: 'max-std'.
    sampler_kwargs : `dict[str, Any]`, optional
        Extra arguments to pass to `bilby.run_sampler()`.
    plot_kwargs : `dict[str, Any]`, optional
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

    if plot_kwargs is None:
        plot_kwargs = {}

    if legend_style not in ["raw", "typeset", "compact"]:
        raise ValueError(f"Invalid legend style: '{legend_style}' (valid options: 'raw', 'typeset', 'compact')")

    if legend_point_estimate not in ["max-std", "med-ci"]:
        raise ValueError(
            f"Invalid legend point estimate: '{legend_point_estimate}' (valid options: 'max-std', 'med-ci')"
        )

    # Conditional imports
    if method == "maximum-likelihood":
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
    elif method == "bayesian-nested-sampling":
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

        if method == "maximum-likelihood":
            fit_result, band_bool = iminuit_fit_spectral_model(
                freqs_MHz,
                bands_MHz,
                fluxs_mJy,
                flux_errs_mJy,
                limit_signs,
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
                limit_signs,
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
                legend_style=legend_style,
            )
        elif method == "bayesian-nested-sampling":
            fit_result = bilby_fit_spectral_model(
                freqs_MHz,
                bands_MHz,
                fluxs_mJy,
                flux_errs_mJy,
                limit_signs,
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
                limit_signs,
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
                legend_style=legend_style,
                legend_point_estimate=legend_point_estimate,
            )
        fit_results[model_name] = fit_result
        plot_dicts[model_name] = plot_dict
        beta_mins[model_name] = beta_min

    if len(fit_results.keys()) == 0:
        return None, None, None, None, None

    # Select the best-fit model out of those fitted
    aic_dict, best_fit_model_name, p_best = select_best_fit_model(beta_mins, len(freqs_MHz))

    if legend_style == "compact":
        legend_inside_bbox = True
    else:
        legend_inside_bbox = False

    # Create spectra plot(s)
    if plot_best:
        # Plot just the best-fit model
        plot_fit(
            freqs_MHz,
            bands_MHz,
            fluxs_mJy,
            flux_errs_mJy,
            limit_signs,
            ref_all,
            plot_dicts[best_fit_model_name],
            save_name=f"{pulsar}_{best_fit_model_name}_{method}_{likelihood}_best_fit.png",
            legend_inside_bbox=legend_inside_bbox,
            append_legend=f"\n$p_\\mathrm{{best}}={p_best:.3f}$",
            **plot_kwargs,
        )
    elif plot_compare:
        # Plot all fitted models side-by-side
        make_comparison_plot(
            freqs_MHz,
            bands_MHz,
            fluxs_mJy,
            flux_errs_mJy,
            limit_signs,
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
                limit_signs,
                ref_all,
                plot_dicts[model_name],
                save_name=f"{pulsar}_{model_name}_{method}_{likelihood}_fit.png",
                legend_inside_bbox=legend_inside_bbox,
                append_legend=f"\n$\\mathrm{{AICc}}={aic_dict[model_name]:.2f}$",
                **plot_kwargs,
            )

    return best_fit_model_name, p_best, fit_results, aic_dict, plot_dicts
