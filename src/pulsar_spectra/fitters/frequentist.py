"""
Functions for using iminuit to fit spectral models.
"""

import logging

import numpy as np
from iminuit import Minuit
from iminuit.cost import LeastSquares
from jacobi import propagate

from ..cost_functions import huber_loss_function, t_loss_function
from ..models import model_settings

logger = logging.getLogger(__name__)


def propagate_flux_n_err(freqs, model, iminuit_result):
    """Propagate the flux based on an input model and use the iminuit to calculate errors if possible.

    Parameters
    ----------
    freqs : `list`
        List of frequencies in MHz.
    model : `function`
        The spectral model function from :py:meth:`pulsar_spectra.models`.
    iminuit_result : `iminuit.Minuit`
        The Minuit class after being fit in :py:meth:`pulsar_spectra.spectral_fit.iminuit_fit_spectral_model`.

    Returns
    -------
    fitted_flux : `list`
        A list of the fluxes (in mJy) based on the input model and fit results.
    fitted_flux_err : `list`
        A list of flux errors (in mJy)  if possible or Nones if not possible.
    """
    if iminuit_result.valid:
        try:
            fitted_flux, fitted_flux_cov = propagate(
                lambda p: model(freqs * 1e6, *p) * 1e3, iminuit_result.values, iminuit_result.covariance
            )
        except ValueError:
            fitted_flux = model(freqs * 1e6, *iminuit_result.values) * 1e3
            fitted_flux_err = [None] * len(fitted_flux)
        else:
            fitted_flux_err = np.diag(fitted_flux_cov) ** 0.5
    else:
        # No convariance values so use old method
        fitted_flux = model(freqs * 1e6, *iminuit_result.values) * 1e3
        fitted_flux_err = [None] * len(fitted_flux)
    return fitted_flux, fitted_flux_err


def migrad_simplex_scan(m, mod_limits, model_name):
    """Find the minimum of least_squares function using the in-built minimisation
    algorithms in iminuit. If migrad by itself fails, then run the simplex
    minimiser before migrad. If simplex fails, run a grid scan over parameter
    space before migrad. Systematically increase the number of calls until
    a valid minimum is found.
    """
    m.tol = 0.00001  # low tolerace improves likelihood of a sensible fit
    m.limits = mod_limits  # limits are primarily to assist the scan minimiser
    ncall = 10000  # Calls until we abandon the fit
    m.migrad(ncall=ncall)
    if m.valid:
        logger.debug(f"Found for fit with {model_name} using migrad and {m.nfcn} calls.")
    else:
        m.simplex(ncall=ncall)
        m.migrad(ncall=ncall)
        if m.valid:
            logger.debug(f"Found for fit with {model_name} using simplex and {m.nfcn} calls.")
        else:
            m.scan(ncall=ncall)
            m.migrad(ncall=ncall)
            if m.valid:
                logger.debug(f"Found for fit with {model_name} using scan and {m.nfcn} calls.")
    if not m.valid:
        logger.warning(f"No valid minimum found for model {model_name} after {m.nfcn} calls.")

    m.hesse()  # accurately computes uncertainties
    logger.debug(model_name)
    logger.debug(m)
    return m


def iminuit_fit_spectral_model(
    freqs_MHz,
    bands_MHz,
    fluxs_mJy,
    flux_errs_mJy,
    model_name="simple_power_law",
    start_params=None,
    mod_limits=None,
    likelihood="Huber",
):
    """Fit pulsar spectra with iminuit.

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
    start_params : `tuple`, optional
        A tuple of the starting parameters for each input to the model that iminuit will use as an initial estimate.
        If none provided, will use the defaults from :py:meth:`pulsar_spectra.models.model_settings`.
    mod_limits : `list` of `tuple`s, optional
        A list of tuples where each tuples is the minimum and maximum limits
        that will be applied to the model by iminuit.
        If none provided, will use the defaults from :py:meth:`pulsar_spectra.models.model_settings`.
    likelihood : `string`, optional
        The distribution to use for the likelihood ('Gaussian', 'Huber', 't'). |br| Default: 'Huber'.

    Returns
    -------
    m : `iminuit.Minuit`
        The Minuit object after being fit in :py:meth:`pulsar_spectra.spectral_fit.iminuit_fit_spectral_model`.
    band_bool : `bool`
        True if bandwidth integration fitting was successful; False otherwise.
    """
    # Reference frequency is the logarithmic centre frequency
    v0_MHz = 10 ** ((np.log10(min(freqs_MHz)) + np.log10(max(freqs_MHz))) / 2)

    # Convert to SI (Hz and Jy) and load into numpy arrays
    v0_Hz = v0_MHz * 1e6
    freqs_Hz = np.array(freqs_MHz, dtype=np.float128) * 1e6
    bands_Hz = np.array(bands_MHz, dtype=np.float128) * 1e6
    fluxs_Jy = np.array(fluxs_mJy, dtype=np.float128) / 1e3
    flux_errs_Jy = np.array(flux_errs_mJy, dtype=np.float128) / 1e3

    # Compute the frequency ranges from the centre frequencies and bandwidths
    min_freqs_Hz = freqs_Hz - bands_Hz / 2
    max_freqs_Hz = freqs_Hz + bands_Hz / 2

    # Load model settings
    model_dict = model_settings()
    num_model_params = len(model_dict[model_name][2])
    model_function = model_dict[model_name][0]
    model_function_integrate = model_dict[model_name][4]

    # Setup start parameters and parameter limits
    if start_params is None:
        start_params = model_dict[model_name][2]
    if mod_limits is None:
        mod_limits = model_dict[model_name][3]

    # Add the reference frequency
    start_params += (v0_Hz,)
    mod_limits += [None]

    # Check the number of degrees of freedom
    if len(freqs_MHz) <= num_model_params + 1:
        logger.warning(f"Only {len(freqs_MHz)} supplied for {model_name} model fit. This is not enough so skipping")
        return None, None

    if (model_name == "high_frequency_cut_off_power_law" or model_name == "double_turn_over_spectrum") and mod_limits[
        0
    ] is None:
        # Set the cut off frequency based on the data set's frequency range
        mod_limits[0] = (max(freqs_Hz), 10 * max(freqs_Hz))
        logger.debug(f"HFCO cut off frequency limits (Hz): {mod_limits[0]}")
        # Replace vc start param with max frequency
        temp_params = list(start_params)
        temp_params[0] = max(freqs_Hz)
        start_params = tuple(temp_params)

    # Define a loss function
    least_squares = LeastSquares(freqs_Hz, fluxs_Jy, flux_errs_Jy, model_function)
    if likelihood == "Gaussian":
        least_squares.loss = "linear"  # Ordinary least squares
    elif likelihood == "Huber":
        least_squares.loss = huber_loss_function
    elif likelihood == "t":
        least_squares.loss = t_loss_function
    else:
        logger.error(f"Invalid likelihood specified: {likelihood}.")
        return None, None

    # Load into Minuit object
    m = Minuit(least_squares, *start_params)
    m.fixed["v0"] = True  # fix the reference frequency

    # Perform the minimisation without bandwidth integration
    m = migrad_simplex_scan(m, mod_limits, model_name)

    if m.valid and (None not in bands_MHz):
        # Fit model with bandwidth intergration correction
        try:
            min_freqs_Hz = freqs_Hz - bands_Hz / 2
            max_freqs_Hz = freqs_Hz + bands_Hz / 2
        except ValueError:
            return None, None

        # Define a loss function
        least_squares = LeastSquares((min_freqs_Hz, max_freqs_Hz), fluxs_Jy, flux_errs_Jy, model_function_integrate)
        if likelihood == "Gaussian":
            least_squares.loss = "linear"  # Ordinary least squares
        elif likelihood == "Huber":
            least_squares.loss = huber_loss_function
        elif likelihood == "t":
            least_squares.loss = t_loss_function
        else:
            logger.error(f"Invalid likelihood specified: {likelihood}.")
            return None, None

        # Set start params as results from first fit
        past_params = ()
        for param in m.values:
            past_params += (param,)
        logger.debug(f"Bandwidth fit params: {past_params}")

        # Load into Minuit object
        m_band = Minuit(least_squares, *past_params)
        m_band.fixed["v0"] = True  # fix the reference frequency

        # Perform the minimisation with bandwidth integration
        try:
            m_band = migrad_simplex_scan(m_band, mod_limits, model_name + "_log")
        except ValueError as verr:
            logger.warning(f"{model_name}_log Value Error: {verr}")
            m_band = m
            band_bool = False
        else:
            band_bool = True

        # Replace the old fit result with the new fit result
        m = m_band
    else:
        band_bool = False
    logger.debug(f"Band bool: {band_bool}")

    return m, band_bool


def iminuit_compute_likelihood(
    freqs_MHz,
    bands_MHz,
    fluxs_mJy,
    flux_errs_mJy,
    iminuit_result,
    model_name,
    band_bool,
    cost_function,
):
    """Select the best-fit model using the AICc.

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
    iminuit_results : `dict`
        A dictionary of fitted `iminuit.Minuit` objects organised by model name.
    band_bool : `bool`
        Whether or not the bandwidth fitting method was used.
    cost_function : `Callable`
        A cost function from :py:meth:`pulsar_spectra.cost_functions`.

    Returns
    -------
    aic_dict : `dict`
        A dictionary of AICc values organised by model name.
    best_fit_model_name : `str`
        The name of the best-fit model from :py:meth:`pulsar_spectra.models`.
    p_best : `float`
        The probability that the selected model is the best-fitting model out
        of the models compared.
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

    # Compute the negative log likelihood
    beta = cost_function(
        model_function(freqs_input_Hz, *iminuit_result.values),
        fluxs_Jy,
        flux_errs_Jy,
    )

    return beta


def iminuit_interpolate_model(
    iminuit_result,
    model_name,
    fitted_freqs,
    band_bool,
):
    """Interpolate iminuit fit to a set of frequencies for plotting.

    Parameters
    ----------
    iminuit_result : `iminuit.Minuit`
        A fitted Minuit object.
    model_name : `str`
        One of the model names from :py:meth:`pulsar_spectra.models.model_settings`.
    fitted_freqs : `list`
        The frequencies to evaluate the model at.
    band_bool : `bool`
        True if bandwidth integration fitting was successful; False otherwise.

    Returns
    -------
    plot_dict : `dict`
        A dictionary of data which will be used for plotting.
    """
    model_dict = model_settings()
    model_function = model_dict[model_name][0]

    fitted_flux, fitted_flux_err = propagate_flux_n_err(
        fitted_freqs,
        model_function,
        iminuit_result,
    )

    # Create string with fit info to put in the legend
    fit_info = [model_name]
    if band_bool:
        fit_info.append("Bandwidth: \u2713")
    else:
        fit_info.append("Bandwidth: \u2718")
    for p, v, e in zip(iminuit_result.parameters, iminuit_result.values, iminuit_result.errors):
        if p.startswith("v"):
            fit_info.append(f"{p} = ${v / 1e6:8.1f} \\pm {e / 1e6:8.1}$ MHz")
        else:
            fit_info.append(f"{p} = ${v:.5f} \\pm {e:.5}$")
    fit_info = "\n".join(fit_info)

    plot_dict = {
        "fit_info": fit_info,
        "fitted_freqs": fitted_freqs,
        "fitted_flux": fitted_flux,
        "error_type": "jacobi",
        "fitted_flux_err": fitted_flux_err,
    }

    return plot_dict
