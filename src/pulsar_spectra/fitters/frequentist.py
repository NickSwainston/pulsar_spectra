"""
Functions for performing frequentist inference of spectral fits.
"""

import logging

import numpy as np
from format_multiple_errors import format_multiple_errors
from iminuit import Minuit
from iminuit.cost import LeastSquares
from jacobi import propagate

from ..cost_functions import huber_loss_function, t_loss_function
from ..models import latex_params, model_settings

logger = logging.getLogger(__name__)


def propagate_flux_n_err(freqs_MHz, model, iminuit_result):
    """Propagate the flux based on an input model and use the iminuit to
    calculate errors if possible.

    Parameters
    ----------
    freqs_MHz : `array_like`
        An array of frequencies in MHz.
    model : `Callable`
        A spectral model function from :py:meth:`pulsar_spectra.models`.
    iminuit_result : `iminuit.Minuit`
        The Minuit class after being fit in
        :py:meth:`pulsar_spectra.spectral_fit.iminuit_fit_spectral_model`.

    Returns
    -------
    fitted_flux : `NDArray[float]`
        A list of the fluxes (in mJy) based on the input model and fit results.
    fitted_flux_err : `NDArray[float]`
        A list of flux errors (in mJy)  if possible or Nones if not possible.
    """
    # Convert to SI (Hz) and load into a numpy array
    freqs_Hz = np.array(freqs_MHz, dtype=float) * 1e6

    if iminuit_result.valid:
        try:
            fitted_flux, fitted_flux_cov = propagate(
                lambda p: model(freqs_Hz, *p) * 1e3, iminuit_result.values, iminuit_result.covariance
            )
        except ValueError:
            fitted_flux = model(freqs_Hz, *iminuit_result.values) * 1e3
            fitted_flux_err = np.empty(len(fitted_flux), dtype=float)
        else:
            fitted_flux_err = np.diag(fitted_flux_cov) ** 0.5
    else:
        # No convariance values so use old method
        fitted_flux = model(freqs_Hz, *iminuit_result.values) * 1e3
        fitted_flux_err = np.empty(len(fitted_flux), dtype=float)
    return fitted_flux, fitted_flux_err


def migrad_simplex_scan(m, mod_limits, model_name="unknown_model", tol=1e-5, ncall=1e4):
    """Minimise a Minuit object using the Migrad algorithm in iminuit. If Migrad
    by itself fails, then run the Simplex algorithm before Migrad. If Simplex
    also fails, then run a grid scan over the parameter space before Migrad.
    Systematically increase the number of calls until a valid minimum is found
    or the call limit has been reached. Lastly, run the Hesse error estimation
    algorithm.

    Parameters
    ----------
    m : `iminuit.Minuit`
        A Minuit object to minimise.
    mod_limit : `list[tuple[float, float]]`
        Constraints on each of the free model parameters. These limits are
        primarily to assist the scan minimiser.
    model_name : `str`, optional
        The model name to use for logging. |br| Default: 'unknown_model'.
    tol : `float`, optional
        Access tolerance for convergence with the EDM criterion. For details.
        see `https://scikit-hep.org/iminuit/reference.html#iminuit.Minuit.tol`.
        |br| Default: 1e-5.
    ncall : `int`, optional
        The number of minimiser calls until the minimisation is abandoned.
        |br| Default: 1e4.
    """
    m.tol = tol
    m.limits = mod_limits
    ncall = int(ncall)
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

    m.hesse()  # Estimate the uncertainties
    logger.debug(model_name)
    logger.debug(m)


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
    """Fit pulsar spectra using iminuit.

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
    start_params : `tuple`, optional
        A tuple of the starting parameter values for each input to the model
        that iminuit will use as an initial estimate.
        |br| Default: Will use the starting parameter values from
        :py:meth:`pulsar_spectra.models.model_settings`.
    mod_limits : `list[tuple[float, float]]`, optional
        Constraints on each of the free model parameters. These limits are
        primarily to assist the scan minimiser.
        |br| Default: Will use the model limits from
        :py:meth:`pulsar_spectra.models.model_settings`.
    likelihood : `str`, optional
        The distribution to use for the likelihood ('Gaussian', 'Huber', 't').
        |br| Default: 'Huber'.

    Returns
    -------
    m : `iminuit.Minuit`
        The Minuit object after being minimised in
        :py:meth:`pulsar_spectra.spectral_fit.iminuit_fit_spectral_model`.
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
    migrad_simplex_scan(m, mod_limits, model_name)

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
            migrad_simplex_scan(m_band, mod_limits, model_name + "_log")
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
    """Compute the cost of the best-fit model.

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
    iminuit_result : `iminuit.Minuit`
        A minimised Minuit object.
    band_bool : `bool`
        Whether or not the bandwidth fitting method was used.
    cost_function : `Callable`
        A cost function from :py:meth:`pulsar_spectra.cost_functions`.

    Returns
    -------
    beta : `float`
        The beta of the best-fit model.
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
    fitted_freqs_MHz,
    band_bool,
    legend_style="raw",
):
    """Interpolate the best-fit model to a set of frequencies for plotting.

    Parameters
    ----------
    iminuit_result : `iminuit.Minuit`
        A minimised Minuit object.
    model_name : `str`
        One of the model names from
        :py:meth:`pulsar_spectra.models.model_settings`.
    fitted_freqs_MHz : `array_like`
        The frequencies in MHz to evaluate the model at.
    band_bool : `bool`
        True if bandwidth integration fitting was successful; False otherwise.
    legend_style : `str`, optional
        The legend style. Either: 'raw', 'typeset', or 'compact'.
        See :py:meth:`pulsar_spectra.spectral_fit.find_best_spectral_fit` for
        further documentation. |br| Default: 'raw'.

    Returns
    -------
    plot_dict : `dict[str, Any]`
        A dictionary of data which will be used for plotting.
    """
    fitted_freqs_MHz = np.array(fitted_freqs_MHz, dtype=float)

    model_dict = model_settings()
    model_function = model_dict[model_name][0]
    short_model_name = model_dict[model_name][1]

    fitted_flux, fitted_flux_err = propagate_flux_n_err(
        fitted_freqs_MHz,
        model_function,
        iminuit_result,
    )

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

    if legend_style == "raw":
        if band_bool:
            fit_info.append("Bandwidth: \u2713")
        else:
            fit_info.append("Bandwidth: \u2718")

    if legend_style in ["raw", "typeset"]:
        for p, v, e in zip(iminuit_result.parameters, iminuit_result.values, iminuit_result.errors):
            # Whether to include units
            if p.startswith("v"):
                v /= 1e6  # Hz -> MHz
                e /= 1e6  # Hz -> MHz
                units_str = " MHz"
            elif p == "c":
                units_str = " mJy"
            else:
                units_str = ""

            # Whether to typeset the parameter names
            if legend_style == "typeset" and p in latex_params:
                lhs_str = f"${latex_params[p]} = "
            else:
                lhs_str = f"{p} = $"

            qty_str = format_multiple_errors(v, e, latex=True)

            fit_info.append(f"{lhs_str}{qty_str}${units_str}")

    fit_info = "\n".join(fit_info)

    plot_dict = {
        "fit_info": fit_info,
        "fitted_freqs": list(fitted_freqs_MHz),
        "fitted_flux": fitted_flux,
        "error_type": "jacobi",
        "fitted_flux_err": fitted_flux_err,
    }

    return plot_dict
