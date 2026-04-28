"""
Functions for performing Bayesian inference of spectral fits.
"""

import inspect
import logging

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from format_multiple_errors import format_multiple_errors

from pulsar_spectra.likelihood_functions import tobit_log_likelihood
from pulsar_spectra.models import latex_params, model_settings

try:
    import bilby
except ModuleNotFoundError as e:
    MSG = "bilby is not installed. To use this feature, install pulsar-spectra[bayesian]."
    raise ModuleNotFoundError(MSG) from e

try:
    import corner
except ModuleNotFoundError as e:
    MSG = "corner is not installed. To use this feature, install pulsar-spectra[bayesian]."
    raise ModuleNotFoundError(MSG) from e


logger = logging.getLogger(__name__)


class TobitLikelihood(bilby.Likelihood):
    def __init__(self, min_max_freqs, fluxs, flux_errs, limit_signs, model_function, loss="Huber"):
        """
        A Tobit likelihood supporting detections and upper/lower limits.
        For detections the standard PDF is used; for limits the CDF is used.
        The parameters are inferred from the arguments of the model function.

        Parameters
        ----------
        min_max_freqs : `tuple[array_like, array_like]` (min_freqs, max_freqs)
            Where min_freqs and max_freqs are arrays containing the minimum and
            maximum frequencies for each measurement.
        fluxs : `array_like`
            The flux density for each measurement.
        flux_errs : `array_like`
            The uncertainty in the flux density for each measurement.
        limit_signs : `array_like`
            Per-point limit flags: +1 lower limit, -1 upper limit, 0 detection.
        model_function : `Callable`
            The model function to fit to the data. The first argument is the
            dependent variable (min/max frequencies), the next arguments
            are the fit parameters and will require a prior, and the last
            argument is the reference frequency.
        loss : `str`, optional
            Distribution to use ('Gaussian', 'Huber', 't'). |br| Default: 'Huber'.
        """
        self.min_max_freqs = min_max_freqs
        self.fluxs = fluxs
        self.flux_errs = flux_errs
        self.limit_signs = np.asarray(limit_signs, dtype=int)
        self.model_function = model_function
        self.loss = loss

        # Infer the parameters from the provided function
        parameters = inspect.getfullargspec(model_function).args
        del parameters[0]
        super().__init__(parameters=dict.fromkeys(parameters))
        self.parameters = dict.fromkeys(parameters)
        self.function_keys = self.parameters.keys()

    def log_likelihood(self):
        model_parameters = {k: self.parameters[k] for k in self.function_keys}
        model_fluxs = self.model_function(self.min_max_freqs, **model_parameters)
        residuals = (self.fluxs - model_fluxs) / self.flux_errs
        return np.sum(tobit_log_likelihood(residuals, self.limit_signs, loss=self.loss))


def bilby_fit_spectral_model(
    freqs_MHz,
    bands_MHz,
    fluxs_mJy,
    flux_errs_mJy,
    limit_signs,
    model_name="simple_power_law",
    mod_priors=None,
    likelihood="Huber",
    sampler="dynamic_dynesty",
    sample="rwalk_dynesty",
    label="unknown_pulsar",
    **sampler_kwargs,
):
    """
    Fit pulsar spectra using the Bilby Bayesian inference library.

    Parameters
    ----------
    freqs_MHz : `array_like`
        An array of the frequencies in MHz.
    bands_MHz : `array_like`
        An array of the bandwidths in MHz.
    fluxs_mJy : `array_like`
        An array of the flux densities in mJy.
    flux_errs_mJy : `array_like`
        An array of the uncertainty in the flux densities in mJy.
    model_name : `str`, optional
        One of the model names from
        :py:meth:`pulsar_spectra.models.model_settings`.
        |br| Default: 'simple_power_law'.
    mod_priors : `dict[str, dict | PriorDict]`, optional
        A dictionary of priors for the free model parameters.
        |br| Default: Will use the priors from
        :py:meth:`pulsar_spectra.models.model_settings`.
    likelihood : `str`, optional
        The distribution to use for the likelihood ('Gaussian', 'Huber', 't').
        |br| Default: 'Huber'.
    sampler : `str`, optional
        The name of the sampler to use. See
        `bilby.sampler.get_implemented_samplers()` for a list of available
        samplers. |br| Default: 'dynamic_dynesty'.
    sample : `str`, optional
        Method used to sample uniformly within the likelihood constraints,
        conditioned on the provided bounds. Will only use this option if the
        Dynesty sampler is being used. See `bilby.core.sampler.Dynesty` for
        additional documentation. |br| Default: 'rwalk_dynesty'.
    label : `str`, optional
        A label to use for the output files; passed to `bilby.run_sampler()`.
        |br| Default: 'unknown_pulsar'.
    **sampler_kwargs
        Extra arguments to pass to `bilby.run_sampler()`.

    Returns
    -------
    bilby_result : `bilby.core.result.Result`
        A Result object containing fit information from
        :py:meth:`pulsar_spectra.fitters.bayesian.bilby_fit_spectral_model`.
    """
    # The reference frequency has been hardcoded so that we can use the known
    # distribution of flux densities at 1400 MHz as a prior
    v0_MHz = 1400.0

    # Convert to SI (Hz and Jy) and load into numpy arrays
    v0_Hz = v0_MHz * 1e6
    freqs_Hz = np.array(freqs_MHz, dtype=np.float64) * 1e6
    bands_Hz = np.array(bands_MHz, dtype=np.float64) * 1e6
    fluxs_Jy = np.array(fluxs_mJy, dtype=np.float64) / 1e3
    flux_errs_Jy = np.array(flux_errs_mJy, dtype=np.float64) / 1e3

    # Compute the frequency ranges from the centre frequencies and bandwidths
    min_freqs_Hz = freqs_Hz - bands_Hz / 2
    max_freqs_Hz = freqs_Hz + bands_Hz / 2

    # Load model settings
    model_dict = model_settings()
    num_model_params = len(model_dict[model_name][2])
    model_function_integrate = model_dict[model_name][4]

    # Setup priors
    if mod_priors is None:
        mod_priors = model_dict[model_name][5]

    # Add the reference frequency
    mod_priors["v0"] = v0_Hz

    # Check the number of degrees of freedom
    if len(freqs_MHz) <= num_model_params + 1:
        logger.warning(f"Only {len(freqs_MHz)} supplied for {model_name} model fit. This is not enough so skipping")
        return None

    if likelihood not in ("Gaussian", "Huber", "t"):
        logger.error(f"Invalid likelihood specified: {likelihood}.")
        return None

    limit_signs = np.asarray(limit_signs, dtype=int)

    L = TobitLikelihood(
        (min_freqs_Hz, max_freqs_Hz),
        fluxs_Jy,
        flux_errs_Jy,
        limit_signs,
        model_function_integrate,
        loss=likelihood,
    )

    # This option is only applicable to the Dynesty sampler
    if sampler in ["dynesty", "dynamic_dynesty"]:
        sampler_kwargs["sample"] = sample

    # Run the sampler
    bilby_result = bilby.run_sampler(
        likelihood=L,
        priors=mod_priors,
        sampler=sampler,
        plot=False,
        check_point_plot=True,
        label=f"{label}_{model_name}_{likelihood}",
        **sampler_kwargs,
    )

    # Make a corner plot
    axes_scales = []
    for param in mod_priors.keys():
        if param == "v0":
            continue
        elif param.startswith("v") or param == "c":
            axes_scales.append("log")
        else:
            axes_scales.append("linear")
    bilby_result.plot_corner(axes_scale=axes_scales)

    return bilby_result


def bilby_compute_maximum_posterior_likelihood(
    freqs_MHz,
    bands_MHz,
    fluxs_mJy,
    flux_errs_mJy,
    limit_signs,
    bilby_result,
    model_name,
    band_bool,
    likelihood="Huber",
):
    """Compute the negative log-likelihood of each posterior sample and find
    the sample with the minimum (i.e. maximum log-likelihood).

    Parameters
    ----------
    freqs_MHz : `array_like`
        An array of the frequencies in MHz.
    bands_MHz : `array_like`
        An array of the bandwidths in MHz.
    fluxs_mJy : `array_like`
        An array of the flux densities in mJy.
    flux_errs_mJy : `array_like`
        An array of the uncertainty in the flux densities in mJy.
    limit_signs : `array_like`
        Per-point limit flags: +1 lower limit, -1 upper limit, 0 detection.
    bilby_result : `dict[str, bilby.Result]`
        A dictionary of `bilby.Result` objects organised by model name.
    model_name : `str`
        One of the model names from
        :py:meth:`pulsar_spectra.models.model_settings`.
    band_bool : `bool`
        Whether or not the bandwidth fitting method was used.
    likelihood : `str`, optional
        Distribution to use ('Gaussian', 'Huber', 't'). |br| Default: 'Huber'.

    Returns
    -------
    beta_min : `float`
        The minimum beta (negative log-likelihood).
    params_beta_min : `dict`
        The parameter values of the minimum beta.
    """
    model_dict = model_settings()

    # Convert to SI (Hz and Jy) and load into numpy arrays
    freqs_Hz = np.array(freqs_MHz, dtype=np.float64) * 1e6
    bands_Hz = np.array(bands_MHz, dtype=np.float64) * 1e6
    fluxs_Jy = np.array(fluxs_mJy, dtype=np.float64) / 1e3
    flux_errs_Jy = np.array(flux_errs_mJy, dtype=np.float64) / 1e3
    limit_signs = np.asarray(limit_signs, dtype=int)

    if band_bool:
        model_function = model_dict[model_name][4]
        freqs_input_Hz = (freqs_Hz - bands_Hz / 2, freqs_Hz + bands_Hz / 2)
    else:
        model_function = model_dict[model_name][0]
        freqs_input_Hz = freqs_Hz

    # Get list of all model parameters
    param_keys = bilby_result.search_parameter_keys + bilby_result.fixed_parameter_keys

    # Get all samples from the posterior
    samples = bilby_result.posterior[param_keys]

    # Compute the negative log-likelihood for each sample (Tobit-aware)
    beta_samples = np.empty(samples.shape[0], dtype=np.float64)
    for isamp in range(samples.shape[0]):
        sample_params = dict(samples.iloc[isamp])
        model_fluxs = model_function(freqs_input_Hz, **sample_params)
        residuals = (fluxs_Jy - model_fluxs) / flux_errs_Jy
        beta_samples[isamp] = -np.sum(tobit_log_likelihood(residuals, limit_signs, loss=likelihood))
    beta_min = np.min(beta_samples)

    # Get the parameter values for the minimised beta
    params_beta_min = dict(samples.iloc[np.argmin(beta_samples)])

    return beta_min, params_beta_min


def bilby_interpolate_model(
    bilby_result,
    model_name,
    fitted_freqs_MHz,
    best_fit_params,
    nsamp=200,
    legend_style="raw",
    legend_point_estimate="max-std",
):
    """
    Determine best fit and raytraces from Bilby posterior samples.

    Parameters
    ----------
    bilby_result : `bilby.core.result.Result`
        A Result object returned by Bilby.
    model_name : `str`
        One of the model names from
        :py:meth:`pulsar_spectra.models.model_settings`.
    fitted_freqs_MHz : `array_like`
        The frequencies in MHz to evaluate the model at.
    best_fit_params : `dict[str, float]`
        A point estimate of the parameter values to add to the plot.
    nsamp : `int`, optional
        The number of posterior samples to plot. |br| Default: 200.
    legend_style : `str`, optional
        The legend style. Either: 'raw', 'typeset', or 'compact'.
        See :py:meth:`pulsar_spectra.spectral_fit.find_best_spectral_fit` for
        further documentation. |br| Default: 'raw'.
    legend_point_estimate : `str`, optional
        The point estimate of the posterior distribution reported in the legend.
        The options are:

            'max-std' : The maximum of each marginal distribution with
            uncertainties equal to 1 standard deviation.

            'med-ci' : The median of each marginal distribution with
            uncertainties calculated from the 68% credible interval.

        |br| Default: 'max-std'.

    Returns
    -------
    plot_dict : `dict[str, Any]`
        A dictionary of data which will be used for plotting.
    """
    fitted_freqs_MHz = np.array(fitted_freqs_MHz, dtype=float)

    model_dict = model_settings()
    model_function = model_dict[model_name][0]
    short_model_name = model_dict[model_name][1]

    param_keys = bilby_result.search_parameter_keys + bilby_result.fixed_parameter_keys

    # Interpolate the best-fit model to the fitted freqs
    best_fit_params_MHz = {}
    for param in best_fit_params.keys():
        # Convert frequencies to MHz
        if param.startswith("v"):
            best_fit_params_MHz[param] = best_fit_params[param] / 1e6
        else:
            best_fit_params_MHz[param] = best_fit_params[param]
    fitted_flux_best = model_function(fitted_freqs_MHz, **best_fit_params_MHz) * 1e3

    # Interpolate to nsamp random samples from the posterior
    samples = bilby_result.posterior[param_keys].sample(nsamp)
    fitted_flux_samples = np.empty(shape=(nsamp, fitted_freqs_MHz.size))
    for isamp in range(nsamp):
        sample_params = dict(samples.iloc[isamp])
        for param in sample_params.keys():
            # Convert frequencies to MHz
            if param.startswith("v"):
                sample_params[param] /= 1e6
        fitted_flux_samples[isamp][:] = model_function(fitted_freqs_MHz, **sample_params) * 1e3

    # Create string with fit info to put in the legend
    fit_info = []
    if legend_style == "raw":
        fit_info.append(model_name)
    elif legend_style == "typeset":
        model_name = model_name.replace("_", " ")
        model_name = model_name.replace("power law", "power-law")
        model_name = model_name.replace("high frequency", "high-frequency")
        model_name = model_name.replace("low frequency", "low-frequency")
        model_name = model_name.replace("cut off", "cut-off")
        model_name = model_name.replace("turn over", "turn-over")
        model_name = model_name.capitalize()
        fit_info.append(model_name)
    elif legend_style == "compact":
        fit_info.append(short_model_name)

    # The Bayesian method always uses bandwidth fitting
    if legend_style == "raw":
        fit_info.append("Bandwidth: \u2713")

    if legend_style in ["raw", "typeset"]:
        params_std = bilby_result.posterior[param_keys].std()
        for param in param_keys:
            # Get point estimates
            p_plus = None
            p_minus = None
            if legend_point_estimate == "max-std":
                # Maximum +- standard deviation
                p_est = best_fit_params[param]
                if param != "v0":
                    p_plus = params_std[param]
                    p_minus = params_std[param]
            elif legend_point_estimate == "med-ci":
                # Median + (68%-50%) - (50%-16%)
                param_range = bilby_result.get_one_dimensional_median_and_error_bar(param)
                p_est = param_range.median
                if param != "v0":
                    p_plus = param_range.plus
                    p_minus = param_range.minus

            # Convert to MHz
            if param.startswith("v"):
                p_est /= 1e6
                if param != "v0":
                    p_plus /= 1e6
                    p_minus /= 1e6

            # Get units
            if param.startswith("v"):
                units_str = " MHz"
            elif param == "c":
                units_str = " mJy"
            else:
                units_str = ""

            # Whether to typeset parameter names
            if legend_style == "typeset" and param in latex_params:
                lhs_str = f"${latex_params[param]} = "
            else:
                lhs_str = f"{param} = $"

            if p_plus is not None and p_minus is not None:
                if np.isclose(p_plus, p_minus, atol=0.0, rtol=0.01):
                    qty_str = format_multiple_errors(p_est, np.mean([p_plus, p_minus]), latex=True)
                else:
                    qty_str = format_multiple_errors(p_est, (p_plus, p_minus), latex=True)
            else:
                qty_str = f"{p_est:.0f}"

            fit_info.append(f"{lhs_str}{qty_str}${units_str}")

    fit_info = "\n".join(fit_info)

    plot_dict = {
        "fit_info": fit_info,
        "fitted_freqs": list(fitted_freqs_MHz),
        "fitted_flux": fitted_flux_best,
        "error_type": "raytrace",
        "fitted_flux_samples": fitted_flux_samples,
    }

    return plot_dict


def bilby_get_model_priors():
    """Get the default model parameter priors for Bayesian fitting.

    Returns
    -------
    priors : `dict[str, PriorDict]`
        A dictionary with model names as keys, where each item is a PriorDict.

    References
    ----------
    Where noted, priors are estimated using distributions from Swainston (2023).
    See: https://espace.curtin.edu.au/handle/20.500.11937/93846
    """
    # NOTE: the Bilby LogNormal priors are the natural log!

    # --- Gain parameter (y-intercept in logspace) ---
    # Log-normal fit to ATNF catalogue S1400 distribution
    c_mean = -1.07
    c_std = 1.61
    c_prior = bilby.core.prior.LogNormal(c_mean, c_std, "c", latex_label="$S_{1400}$", unit="mJy")

    # --- Spectral index (gradient in logspace) ---
    # Normal fit to the pulsar population spectral index distribution
    # See Table 6.4 of Swainston (2023)
    a_mean = -1.61
    a_std = 0.74
    a_prior = bilby.core.prior.Normal(a_mean, a_std, "a", latex_label="$\\alpha$")
    a1_prior = bilby.core.prior.Normal(a_mean, a_std, "a1", latex_label="$\\alpha_1$")
    a2_prior = bilby.core.prior.Normal(a_mean, a_std, "a2", latex_label="$\\alpha_2$")

    # --- The smoothness of the low-frequency turn-over, beta ---
    # Note that beta=2.1 corresponds to the case of free-free absorption
    beta_min = 0.1
    beta_max = 2.1
    beta_prior = bilby.core.prior.Uniform(beta_min, beta_max, "beta", latex_label="$\\beta$")

    # --- The frequency of the high-frequency cut-off ---
    # Estimated based on the pulsar population HF cutoff distribution
    # See Figure 6.4 of Swainston (2023)
    vc_mean = 22.33  # 5 GHz
    vc_std = 1.0
    vc_prior = bilby.core.prior.LogNormal(vc_mean, vc_std, "vc", latex_label="$\\nu_\\mathrm{c}$", unit="Hz")

    # --- The peak frequency of the low-frequency turn-over ---
    # A broad prior based the literature
    vpeak_mean = 18.42  # 100 MHz
    vpeak_std = 0.7
    vpeak_prior = bilby.core.prior.LogNormal(
        vpeak_mean, vpeak_std, "vpeak", latex_label="$\\nu_\\mathrm{peak}$", unit="Hz"
    )

    # --- The break frequency of the broken power-law ---
    # A broad prior based the literature
    vbreak_mean = 20.36  # 700 MHz
    vbreak_std = 1.0
    vbreak_prior = bilby.core.prior.LogNormal(
        vbreak_mean, vbreak_std, "vb", latex_label="$\\nu_\\mathrm{b}$", unit="Hz"
    )

    priors = {
        "simple_power_law": bilby.core.prior.PriorDict(
            {
                "a": a_prior,
                "c": c_prior,
            }
        ),
        "broken_power_law": bilby.core.prior.PriorDict(
            {
                "vb": vbreak_prior,
                "a1": a1_prior,
                "a2": a2_prior,
                "c": c_prior,
            }
        ),
        "high_frequency_cut_off_power_law": bilby.core.prior.PriorDict(
            {
                "vc": vc_prior,
                "a": a_prior,
                "c": c_prior,
            }
        ),
        "low_frequency_turn_over_power_law": bilby.core.prior.PriorDict(
            {
                "vpeak": vpeak_prior,
                "a": a_prior,
                "c": c_prior,
                "beta": beta_prior,
            }
        ),
        "double_turn_over_spectrum": bilby.core.prior.PriorDict(
            {
                "vc": vc_prior,
                "vpeak": vpeak_prior,
                "a": a_prior,
                "beta": beta_prior,
                "c": c_prior,
            }
        ),
    }

    return priors


def prior_predictive_check(nsamp=1000):
    """Perform a prior predictive check by generating samples from the prior
    distribution and making spectra and corner plots to visualise the samples.

    Parameters
    ----------
    nsamp : `int`, optional
        The number of samples to generate from the prior distribution.
        |br| Default: 1000.
    """
    model_dict = model_settings()

    freqs_MHz = np.logspace(1, 5, 1000)

    for model_name in model_dict.keys():
        model_func = model_dict[model_name][0]
        model_priors = model_dict[model_name][5]

        samples = pd.DataFrame(model_priors.sample(nsamp))
        axes_scales = []
        latex_labels = []
        for param in model_priors.keys():
            if param.startswith("v") or param == "c":
                axes_scales.append("log")
            else:
                axes_scales.append("linear")
            latex_labels.append(model_priors[param].latex_label_with_unit)

        fig = corner.corner(samples, axes_scale=axes_scales, labels=latex_labels)
        plt.savefig(f"prior_corner_{model_name}.png")
        plt.close()

        model_priors["v0"] = 1400e6
        samples = pd.DataFrame(model_priors.sample(nsamp))
        fig, ax = plt.subplots(dpi=300, tight_layout=True)
        for isamp in range(nsamp):
            sample_params = dict(samples.iloc[isamp])

            # Convert the frequencies back to MHz
            for param in sample_params.keys():
                if param.startswith("v"):
                    sample_params[param] /= 1e6

            # Interpolate the sample model to the fitted freqs
            flux_density_mJy = model_func(freqs_MHz, **sample_params) * 1e3

            # Add raytrace to plot
            ax.plot(freqs_MHz, flux_density_mJy, "k", marker="None", ls="-", lw=0.2, alpha=0.2)

        ax.set_xscale("log")
        ax.set_yscale("log")
        ax.set_ylim([1e-1, 1e5])
        ax.tick_params(which="both", direction="in", top=1, right=1)
        ax.set_xlabel("Frequency (MHz)")
        ax.set_ylabel("Flux Density (mJy)")

        fig.savefig(f"prior_predictive_check_{model_name}.png")
        plt.close()
