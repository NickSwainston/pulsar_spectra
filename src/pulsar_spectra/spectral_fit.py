"""
The top-level function for finding the best-fit spectral model.
"""

import logging
from dataclasses import dataclass, field
from importlib.metadata import version as _importlib_version

import numpy as np

from pulsar_spectra.model_selection import select_best_fit_model
from pulsar_spectra.models import model_settings
from pulsar_spectra.plotting import make_comparison_plot, plot_fit

logger = logging.getLogger(__name__)

_PULSAR_SPECTRA_VERSION = _importlib_version("pulsar_spectra")


@dataclass
class SpectralFitResult:
    """Fitter-agnostic summary of the best-fit spectral model.

    Frequency parameters (``v*``) are in MHz; the flux density normalisation
    (``c``) is in mJy; all other parameters are dimensionless. Raw fitter
    objects are preserved in ``fit_results`` for advanced use.

    Attributes
    ----------
    pulsar : str
        Name of the pulsar.
    model : str
        Name of the best-fit model from
        :py:meth:`pulsar_spectra.models.model_settings`.
    method : str
        Fitting method: ``'maximum-likelihood'`` or
        ``'bayesian-nested-sampling'``.
    likelihood : str
        Likelihood function: ``'Gaussian'``, ``'Huber'``, or ``'t'``.
    p_best : float
        Akaike probability that this is the best model among those compared.
    params : dict
        Best-fit parameter values in user-facing units. Frequency parameters
        (names starting with ``v``) are in MHz; the flux density
        normalisation ``c`` is in mJy; all others are dimensionless.
    param_errs : dict
        Symmetric 1-sigma parameter uncertainties in the same units as
        ``params``. For maximum-likelihood these are Hesse errors; for
        Bayesian nested sampling they are posterior standard deviations.
    aic : float
        AICc value for the best-fit model.
    aic_dict : dict
        AICc values for every fitted model, keyed by model name.
    n_data : int
        Number of data points used in the fit.
    band_bool : bool
        Whether bandwidth integration was applied to the best-fit model.
    exclude_models : list
        Model names that were excluded from the comparison.
    pulsar_spectra_version : str
        Version string of ``pulsar_spectra`` at the time of fitting,
        useful for reproducibility.
    fit_results : dict
        Raw fitter objects keyed by model name (``iminuit.Minuit`` for
        maximum-likelihood, ``bilby.core.result.Result`` for Bayesian
        nested sampling). Preserved for advanced post-processing.
    plot_dicts : dict
        Plot data dicts keyed by model name, passed directly to
        :py:meth:`pulsar_spectra.plotting.plot_fit`.
    """

    pulsar: str
    model: str
    method: str
    likelihood: str
    p_best: float
    params: dict
    param_errs: dict
    aic: float
    aic_dict: dict
    n_data: int
    band_bool: bool
    exclude_models: list
    pulsar_spectra_version: str
    fit_results: dict = field(default_factory=dict)
    plot_dicts: dict = field(default_factory=dict)

    def to_dict(self):
        """Serialise the result to a plain Python dict suitable for JSON or YAML output.

        Raw fitter objects (``fit_results``, ``plot_dicts``) are excluded because
        they are not serialisable.  All numeric values are converted to Python
        floats so the output round-trips through JSON and PyYAML without issue.
        """
        return {
            "pulsar": self.pulsar,
            "model": self.model,
            "method": self.method,
            "likelihood": self.likelihood,
            "p_best": float(self.p_best),
            "params": {k: float(v) for k, v in self.params.items()},
            "param_errs": {k: float(v) for k, v in self.param_errs.items()},
            "aic": float(self.aic),
            "aic_dict": {k: float(v) for k, v in self.aic_dict.items()},
            "n_data": int(self.n_data),
            "band_bool": bool(self.band_bool),
            "exclude_models": list(self.exclude_models),
            "pulsar_spectra_version": self.pulsar_spectra_version,
        }


def _iminuit_params_to_user_units(m):
    """Return (params, param_errs) dicts from a Minuit result in user-facing units."""
    params = {}
    param_errs = {}
    for p in m.parameters:
        v = m.values[p]
        e = m.errors[p]
        if p.startswith("v"):
            params[p] = v / 1e6
            param_errs[p] = e / 1e6
        elif p == "c":
            params[p] = v * 1e3
            param_errs[p] = e * 1e3
        else:
            params[p] = v
            param_errs[p] = e
    return params, param_errs


def _bilby_params_to_user_units(map_params, bilby_result):
    """Return (params, param_errs) dicts from a Bilby MAP estimate in user-facing units.

    Point estimates come from ``map_params`` (the posterior sample with the
    maximum likelihood); uncertainties are the posterior standard deviations.
    """
    params = {}
    param_errs = {}
    param_keys = bilby_result.search_parameter_keys + bilby_result.fixed_parameter_keys
    params_std = bilby_result.posterior[param_keys].std()
    for p, v in map_params.items():
        e = float(params_std.get(p, 0.0))
        if p.startswith("v"):
            params[p] = v / 1e6
            param_errs[p] = e / 1e6
        elif p == "c":
            params[p] = v * 1e3
            param_errs[p] = e * 1e3
        else:
            params[p] = v
            param_errs[p] = e
    return params, param_errs


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
    result : `SpectralFitResult` or `None`
        A fitter-agnostic summary of the best-fit model, or ``None`` if no
        model could be fitted.  Key attributes:

        * ``pulsar`` — pulsar name.
        * ``model`` — best-fit model name.
        * ``method`` / ``likelihood`` — settings used.
        * ``p_best`` — Akaike probability of the best model.
        * ``params`` / ``param_errs`` — best-fit values and symmetric
          uncertainties in user-facing units (MHz for frequencies, mJy for
          the flux density normalisation ``c``).
        * ``aic`` / ``aic_dict`` — AICc of the best model and all models.
        * ``n_data`` — number of data points.
        * ``band_bool`` — whether bandwidth integration was used.
        * ``exclude_models`` — model names excluded from comparison.
        * ``pulsar_spectra_version`` — software version string.
        * ``fit_results`` — raw fitter objects keyed by model name
          (``iminuit.Minuit`` or ``bilby.core.result.Result``).
        * ``plot_dicts`` — plot data dicts keyed by model name.
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
        from pulsar_spectra.fitters.frequentist import (
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
        from pulsar_spectra.fitters.bayesian import (
            bilby_compute_maximum_posterior_likelihood,
            bilby_fit_spectral_model,
            bilby_interpolate_model,
        )
    else:
        logger.error(f"Invalid fitting method: {method}.")
        return None

    if likelihood not in ("Gaussian", "Huber", "t"):
        logger.error(f"Invalid likelihood: {likelihood}.")
        return None

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
    band_bool_dict = {}
    map_params_dict = {}  # Bayesian MAP parameter estimates, keyed by model name
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
                likelihood=likelihood,
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
                likelihood=likelihood,
            )
            map_params_dict[model_name] = params_beta_min
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
        band_bool_dict[model_name] = band_bool

    if len(fit_results.keys()) == 0:
        return None

    # Select the best-fit model out of those fitted
    aic_dict, best_fit_model_name, p_best = select_best_fit_model(beta_mins, len(freqs_MHz))

    # Extract best-fit parameters in a fitter-agnostic format
    if method == "maximum-likelihood":
        params, param_errs = _iminuit_params_to_user_units(fit_results[best_fit_model_name])
    else:
        params, param_errs = _bilby_params_to_user_units(
            map_params_dict[best_fit_model_name], fit_results[best_fit_model_name]
        )

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

    return SpectralFitResult(
        pulsar=pulsar,
        model=best_fit_model_name,
        method=method,
        likelihood=likelihood,
        p_best=p_best,
        params=params,
        param_errs=param_errs,
        aic=aic_dict[best_fit_model_name],
        aic_dict=aic_dict,
        n_data=len(freqs_MHz),
        band_bool=band_bool_dict[best_fit_model_name],
        exclude_models=exclude_models,
        pulsar_spectra_version=_PULSAR_SPECTRA_VERSION,
        fit_results=fit_results,
        plot_dicts=plot_dicts,
    )
