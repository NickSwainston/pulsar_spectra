"""
Functions for performing Bayesian inference of spectral fits.
"""

import inspect
import logging

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from ..cost_functions import gaussian_cost_function, huber_cost_function, t_cost_function
from ..models import model_settings

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


class GaussianLikelihood(bilby.Likelihood):
    def __init__(self, min_max_freqs, fluxs, flux_errs, model_function):
        """
        A Gaussian likelihood. The parameters are inferred from the arguments
        of the function.

        Parameters
        ----------
        min_max_freqs : `tuple[array_like, array_like]` (min_freqs, max_freqs)
            Where min_freqs and max_freqs are arrays containing the minimum and
            maximum frequencies for each measurement.
        fluxs : `array_like`
            The flux density for each measurement.
        flux_errs : `array_like`
            The uncertainty in the flux density for each measurement.
        function : `Callable`
            The model function to fit to the data. The first argument is the
            dependent variable (min/max frequencies), the next arguments
            are the fit parameters and will require a prior, and the last
            argument is the reference frequency.
        """
        self.min_max_freqs = min_max_freqs
        self.fluxs = fluxs
        self.flux_errs = flux_errs
        self.model_function = model_function

        # Infer the parameters from the provided function
        parameters = inspect.getfullargspec(model_function).args
        del parameters[0]
        super().__init__(parameters=dict.fromkeys(parameters))
        self.parameters = dict.fromkeys(parameters)
        self.function_keys = self.parameters.keys()

    def log_likelihood(self):
        model_parameters = {k: self.parameters[k] for k in self.function_keys}
        model_fluxs = self.model_function(self.min_max_freqs, **model_parameters)
        return -1.0 * gaussian_cost_function(model_fluxs, self.fluxs, self.flux_errs)


class HuberLikelihood(bilby.Likelihood):
    def __init__(self, min_max_freqs, fluxs, flux_errs, model_function):
        """
        A modified Gaussian likelihood which transitions to linear loss at a set
        deviation from the model. The parameters are inferred from the arguments
        of the function.

        Parameters
        ----------
        min_max_freqs : `tuple[array_like, array_like]` (min_freqs, max_freqs)
            Where min_freqs and max_freqs are arrays containing the minimum and
            maximum frequencies for each measurement.
        fluxs : `array_like`
            The flux density for each measurement.
        flux_errs : `array_like`
            The uncertainty in the flux density for each measurement.
        function : `Callable`
            The model function to fit to the data. The first argument is the
            dependent variable (min/max frequencies), the next arguments
            are the fit parameters and will require a prior, and the last
            argument is the reference frequency.
        """
        self.min_max_freqs = min_max_freqs
        self.fluxs = fluxs
        self.flux_errs = flux_errs
        self.model_function = model_function

        # Infer the parameters from the provided function
        parameters = inspect.getfullargspec(model_function).args
        del parameters[0]
        super().__init__(parameters=dict.fromkeys(parameters))
        self.parameters = dict.fromkeys(parameters)
        self.function_keys = self.parameters.keys()

    def log_likelihood(self):
        model_parameters = {k: self.parameters[k] for k in self.function_keys}
        model_fluxs = self.model_function(self.min_max_freqs, **model_parameters)
        return -1.0 * huber_cost_function(model_fluxs, self.fluxs, self.flux_errs)


class TLikelihood(bilby.Likelihood):
    def __init__(self, min_max_freqs, fluxs, flux_errs, model_function):
        """
        A t-distribution likelihood. The parameters are inferred from the
        arguments of the function.

        Parameters
        ----------
        min_max_freqs : `tuple[array_like, array_like]` (min_freqs, max_freqs)
            Where min_freqs and max_freqs are arrays containing the minimum and
            maximum frequencies for each measurement.
        fluxs : `array_like`
            The flux density for each measurement.
        flux_errs : `array_like`
            The uncertainty in the flux density for each measurement.
        function : `Callable`
            The model function to fit to the data. The first argument is the
            dependent variable (min/max frequencies), the next arguments
            are the fit parameters and will require a prior, and the last
            argument is the reference frequency.
        """
        self.min_max_freqs = min_max_freqs
        self.fluxs = fluxs
        self.flux_errs = flux_errs
        self.model_function = model_function

        # Infer the parameters from the provided function
        parameters = inspect.getfullargspec(model_function).args
        del parameters[0]
        super().__init__(parameters=dict.fromkeys(parameters))
        self.parameters = dict.fromkeys(parameters)
        self.function_keys = self.parameters.keys()

        # Degrees of freedom
        self.df = 4

    def log_likelihood(self):
        model_parameters = {k: self.parameters[k] for k in self.function_keys}
        model_fluxs = self.model_function(self.min_max_freqs, **model_parameters)
        return -1.0 * t_cost_function(model_fluxs, self.fluxs, self.flux_errs, self.df)


def bilby_fit_spectral_model(
    freqs_MHz,
    bands_MHz,
    fluxs_mJy,
    flux_errs_mJy,
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

    # Choose the likelihood class
    if likelihood == "Gaussian":
        Likelihood = GaussianLikelihood
    elif likelihood == "Huber":
        Likelihood = HuberLikelihood
    elif likelihood == "t":
        Likelihood = TLikelihood
    else:
        logger.error(f"Invalid likelihood specified: {likelihood}.")
        return None

    # Define the likelihood
    L = Likelihood(
        (min_freqs_Hz, max_freqs_Hz),
        fluxs_Jy,
        flux_errs_Jy,
        model_function_integrate,
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
        label=f"{label}_{model_name}",
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
    bilby_result,
    model_name,
    band_bool,
    cost_function,
):
    """Compute the cost of each posterior sample and find the sample with the
    minimum cost (i.e. maximum log-likelihood).

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
    bilby_result : `dict[str, bilby.Result]`
        A dictionary of `bilby.Result` objects organised by model name.
    model_name : `str`
        One of the model names from
        :py:meth:`pulsar_spectra.models.model_settings`.
    band_bool : `bool`
        Whether or not the bandwidth fitting method was used.
    cost_function : `Callable`
        A cost function from :py:meth:`pulsar_spectra.cost_functions`.

    Returns
    -------
    beta_min : `float`
        The minimum beta (negative log-likelihood).
    params_beta_min : `dict`
        The parameter values of the minimum beta.
    """
    model_dict = model_settings()

    # Convert to SI (Hz and Jy) and load into numpy arrays
    freqs_Hz = np.array(freqs_MHz, dtype=np.float128) * 1e6
    bands_Hz = np.array(bands_MHz, dtype=np.float128) * 1e6
    fluxs_Jy = np.array(fluxs_mJy, dtype=np.float128) / 1e3
    flux_errs_Jy = np.array(flux_errs_mJy, dtype=np.float128) / 1e3

    if band_bool:
        model_function = model_dict[model_name][4]
        freqs_input_Hz = (freqs_Hz - bands_Hz / 2, freqs_Hz + bands_Hz / 2)
    else:
        model_function = model_dict[model_name][0]
        freqs_input_Hz = freqs_Hz

    # Get list of all model parameters
    param_keys = bilby_result.search_parameter_keys + bilby_result.fixed_parameter_keys

    # Get nsamp samples from the posterior
    samples = bilby_result.posterior[param_keys]

    # Compute the minimised negative log likelihood for each sample
    beta_samples = np.empty(samples.shape[0], dtype=np.float64)
    for isamp in range(samples.shape[0]):
        sample_params = dict(samples.iloc[isamp])
        beta_samples[isamp] = cost_function(
            model_function(freqs_input_Hz, **sample_params),
            fluxs_Jy,
            flux_errs_Jy,
        )
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

    Returns
    -------
    plot_dict : `dict[str, Any]`
        A dictionary of data which will be used for plotting.
    """
    fitted_freqs_MHz = np.array(fitted_freqs_MHz, dtype=float)

    model_dict = model_settings()
    model_function = model_dict[model_name][0]

    param_keys = bilby_result.search_parameter_keys + bilby_result.fixed_parameter_keys

    # Interpolate the best-fit model to the fitted freqs
    for param in best_fit_params.keys():
        # Convert frequencies to MHz
        if param.startswith("v"):
            best_fit_params[param] /= 1e6
    fitted_flux_best = model_function(fitted_freqs_MHz, **best_fit_params) * 1e3

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
    fit_info = [model_name]
    fit_info.append("Bandwidth: \u2713")
    for param in param_keys:
        param_range = bilby_result.get_one_dimensional_median_and_error_bar(param)
        if param == "v0":
            fit_info.append(f"{param} = ${param_range.median / 1e6:.2f}$ MHz")
        elif param.startswith("v"):
            fit_info.append(
                f"{param} = ${param_range.median / 1e6:.2f}"
                + f"^{{+{param_range.plus / 1e6:.2f}}}_{{-{param_range.minus / 1e6:.2f}}}$ MHz"
            )
        else:
            fit_info.append(f"{param} = {param_range.string}")
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
