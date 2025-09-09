"""
Functions for using Bilby to fit spectral models.
"""

import inspect
import logging

import bilby
import numpy as np

from ..cost_functions import gaussian_cost_function, huber_cost_function, t_cost_function
from ..models import model_settings

logger = logging.getLogger(__name__)


class GaussianLikelihood(bilby.Likelihood):
    def __init__(self, min_max_freqs, fluxs, flux_errs, model_function):
        """
        A Gaussian likelihood. The parameters are inferred from the arguments
        of the function.

        Parameters
        ----------
        min_max_freqs: `tuple` (min_freqs, max_freqs)
            Where min_freqs and max_freqs are arrays containing the minimum and
            maximum frequencies for each measurement.
        fluxs: array_like
            The flux density for each measurement.
        flux_errs: array_like
            The uncertainty in the flux density for each measurement.
        function:
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
        min_max_freqs: `tuple` (min_freqs, max_freqs)
            Where min_freqs and max_freqs are arrays containing the minimum and
            maximum frequencies for each measurement.
        fluxs: array_like
            The flux density for each measurement.
        flux_errs: array_like
            The uncertainty in the flux density for each measurement.
        function:
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
        A t-distribution likelihood. The parameters are inferred from the arguments
        of the function.

        Parameters
        ----------
        min_max_freqs: `tuple` (min_freqs, max_freqs)
            Where min_freqs and max_freqs are arrays containing the minimum and
            maximum frequencies for each measurement.
        fluxs: array_like
            The flux density for each measurement.
        flux_errs: array_like
            The uncertainty in the flux density for each measurement.
        function:
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
    label="unknown_pulsar",
):
    """
    Fit pulsar spectra using Bilby and the Dynesty dynamic nested sampler.

    Parameters
    ----------
    freqs_MHz : `list`
        A list of the frequencies in MHz.
    bands_MHz : `list`
        A list of the bandwidths in MHz.
    fluxs_mJy : `list`
        A list of the flux densities in mJy.
    flux_errs_mJy : `list`
        A list of the uncertainty in the flux densities in mJy.
    model_name : `function`, optional
        One of the model names from :py:meth:`pulsar_spectra.models.model_settings`.
        Default: :py:meth:`pulsar_spectra.models.simple_power_law`.
    mod_priors : `dict`, optional
        A dictionary of model priors to pass to Bilby.
        If none provided, will use the defaults from :py:meth:`pulsar_spectra.models.model_settings`.
    likelihood : `string`, optional
        The distribution to use for the likelihood ('Gaussian', 'Huber', 't'). |br| Default: 'Huber'.
    label : `string`, optional
        A label to use for the model fit, given to `bilby.run_sampler()`. |br| Default: 'unknown_pulsar'.

    Returns
    -------
    bilby_result : `bilby.core.result.Result`
        A Result object containing fit information from :py:meth:`pulsar_spectra.bayesian.bilby_fit_spectral_model`.
    """
    # Reference frequency
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

    # Run the dynamic nested sampler
    bilby_result = bilby.run_sampler(
        likelihood=L,
        priors=mod_priors,
        sampler="dynamic_dynesty",
        sample="rwalk_dynesty",
        plot=False,
        check_point_plot=True,
        label=f"{label}_{model_name}",
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
    freqs_MHz : `list`
        A list of the frequencies in MHz.
    bands_MHz : `list`
        A list of the bandwidths in MHz.
    fluxs_mJy : `list`
        A list of the flux densities in mJy.
    flux_errs_mJy : `list`
        A list of the uncertainty in the flux densities in mJy.
    bilby_result : `dict`
        A dictionary of `bilby.Result` objects organised by model name.
    model_name : `str`
        One of the model names from :py:meth:`pulsar_spectra.models.model_settings`.
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
    fitted_freq,
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
        One of the model names from :py:meth:`pulsar_spectra.models.model_settings`.
    fitted_freqs : `list`
        The frequencies to evaluate the model at.
    best_fit_params : `dict`
        A point estimate of the parameter values to add to the plot.
    nsamp : `int`, optional
        The number of posterior samples to plot.

    Returns
    -------
    plot_dict : `dict`
        A dictionary of data which will be used for plotting.
    """
    model_dict = model_settings()
    model_function = model_dict[model_name][0]

    param_keys = bilby_result.search_parameter_keys + bilby_result.fixed_parameter_keys

    # Interpolate the best-fit model to the fitted freqs
    for param in best_fit_params.keys():
        # Convert frequencies to MHz
        if param.startswith("v"):
            best_fit_params[param] /= 1e6
    fitted_flux_best = model_function(fitted_freq, **best_fit_params) * 1e3

    # Interpolate to nsamp random samples from the posterior
    samples = bilby_result.posterior[param_keys].sample(nsamp)
    fitted_flux_samples = np.empty(shape=(nsamp, fitted_freq.size))
    for isamp in range(nsamp):
        sample_params = dict(samples.iloc[isamp])
        for param in sample_params.keys():
            # Convert frequencies to MHz
            if param.startswith("v"):
                sample_params[param] /= 1e6
        fitted_flux_samples[isamp][:] = model_function(fitted_freq, **sample_params) * 1e3

    # Create string with fit info to put in the legend
    fit_info = [model_name]
    fit_info.append("Bandwidth: \u2713")
    for param in param_keys:
        param_range = bilby_result.get_one_dimensional_median_and_error_bar(param)
        if param == "v0":
            fit_info.append(f"{param} = ${param_range.median / 1e6:.2f}$ MHz")
        elif param.startswith("v"):
            fit_info.append(
                f"{param} = ${param_range.median / 1e6:.2f}^{{+{param_range.plus / 1e6:.2f}}}_{{-{param_range.minus / 1e6:.2f}}}$ MHz"  # noqa: E501
            )
        else:
            fit_info.append(f"{param} = {param_range.string}")
    fit_info = "\n".join(fit_info)

    plot_dict = {
        "fit_info": fit_info,
        "fitted_freqs": fitted_freq,
        "fitted_flux": fitted_flux_best,
        "error_type": "raytrace",
        "fitted_flux_samples": fitted_flux_samples,
    }

    return plot_dict
